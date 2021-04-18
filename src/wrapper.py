import os

import numpy
from psycopg2.extensions import register_adapter, AsIs

from numpy.core.numeric import identity
import datetime

from database_driver.database_conn import *
from calculations.java_input_csv_OSM import create_input_file , prepare_java_file
from calculations.calculation_route_eez_intersection import compute_routes_length
from calculations.calculation_risk_model import geo_risk, chokepoint_risk
from parsers.parser_strait import parse_strait
from parsers.parser_pipeline import *
from parsers.parser_wgi import *
from parsers.parser_alphatanker import *
from parsers.parser_piracy import piracy_by_year
from parsers.parser_lvh import parse_LVH

############################CONFIGURATION FLAGS############################
###########################################################################
flag_insert_lvh = 0
lvh_file = "../input_data_spreadsheet/commodity AT_GDP.xlsx"

flag_insert_straits = 0
strait_file = '../input_data_spreadsheet/straits_country.xlsx'

flag_insert_pipelines = 0
pipeline_file = '../input_data_spreadsheet/pipeline_info.xlsx'

flag_insert_approx_pipelines = 0
approx_pipeline_file = '../input_data_spreadsheet/surface_area_country.xls'

flag_insert_wgi = 0
wgi_file = "../input_data_spreadsheet/wgidataset.xlsx"
wgi_year = 2019

flag_insert_piracy = 0
piracy_file = '../input_data_spreadsheet/2019 Stable Seas Index Data(OEF).xlsx'
piracy_year = 2019

flag_geo_risk = 0
geo_risk_year = 2019

flag_ck_risk = 0
ck_risk_year = 2019

flag_intake = 1
alphatanker_file = '../input_data_spreadsheet/4_export_prova_alph.xlsx'

#########################-----ADAPT-----######################################
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)

register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)

##############################################################################
conn = connect()

############### RUN ONCE ####################

#Insertion of LVH data (Need file path)
if flag_insert_lvh == 1:
    lvh = parse_LVH(lvh_file)
    insert_into(conn, 'commodity_lvh', lvh)
    x,_ = get_values(conn, 'commodity_lvh')
    print(x.head(10))

#Insertion of Chokepoints on both tables
if flag_insert_straits == 1:
    names, name_country = parse_strait(strait_file)
    insert_into(conn, 'chokepoint', names)

    for key, value in name_country.items():
        for country in value:
            if type(country) != float: #Filter NaN from the list 
                where_clause = "strait_name=%s" % repr(key)
                id,_ = get_values(conn, 'chokepoint', 'chokepoint_id', where_clause)
                id['country'] =[country] #
                insert_into(conn, 'country_chokepoint', id)

#Insertion of pipelines -> Disclaimer: Since there is not info of the pipelines the sqrt(surface in km2) is used only Egypt, Libya and Iraq has an accurate value
if flag_insert_pipelines == 1:
    pipe_lines = parse_pipeline(pipeline_file)
    insert_into(conn, 'pipeline', pipe_lines)

    country_pipes = parse_pipeline_country(pipeline_file)

    for index,row in country_pipes.iterrows():
        where_clause = "name=%s" % repr(row['pipeline name'])
        id,_ = get_values(conn, 'pipeline','pipeline_id', where_clause)
        id['country'], id['length'], = [row['country'], row['length']]
        insert_into(conn, 'country_pipeline', id)

if flag_insert_approx_pipelines == 1:
    approx_pipelines = parse_surface(approx_pipeline_file)
    insert_into(conn, 'pipeline', approx_pipelines)

    for index,row in approx_pipelines.iterrows():
        where_clause = "name=%s" % repr(row['name'])
        id,_ = get_values(conn, 'pipeline','pipeline_id', where_clause)
        id['country'], id['length'], = [row['load_port'], row['total_length']]
        insert_into(conn, 'country_pipeline', id)
    
############# RUN ONCE A YEAR #################

#Insertion of WGI data (Needs= path of the file, year)
if flag_insert_wgi == 1 and wgi_year != 0:
    wgi = wgi_by_year(wgi_file, wgi_year)
    insert_into(conn, 'wgi', wgi)
    x,_ = get_values(conn, 'wgi', 'country, year, rule_of_law', "country='Armenia'")
    print(x.head(10))


#Insertion of Piracy Parser data (Needs= path of the file, year)

if flag_insert_piracy == 1 and piracy_year!= 0:
    piracy = piracy_by_year(piracy_file, piracy_year)
    insert_into(conn, 'piracy_index', piracy)
    x,_ = get_values(conn, 'piracy_index')
    print(x.head(10))

if flag_geo_risk == 1 and geo_risk_year!=0:
    geo_risk_df = geo_risk(conn, str(geo_risk_year))
    print(geo_risk_df.head(10))
    insert_into(conn, 'geo_risk', geo_risk_df)

if flag_ck_risk == 1 and ck_risk_year!=0:
    x = chokepoint_risk(conn, str(ck_risk_year))
    print(x.head(15))
    insert_into(conn,'chokepoint_risk',x)

############# RUN OFTEN ################

#Add Corridor and Alphatanker intakes
if flag_intake == 1:
    
    print("------Creating Java Input File-------")
    create_input_file(alphatanker_file)

    #run Java Sea Route
    print("------Running external searoute.java-------")
    time =  datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    os.system("java -jar searoute-2.1/searoute.jar -i java_input.csv -res 5 -panama 0 -o ./shape_files/new_route_%s/out.shp" % time)

    #Prepare java file as df to added to corridor table
    corridor_df, pipe_lines = prepare_java_file('java_input.csv')

    #Add Corridor to database 
    print("------Insert into Corridor-------")
    insert_into(conn, 'corridor', corridor_df)
    
    #Run Intersecction 
    sea_length, straits = compute_routes_length("shape_files/new_route_%s/out.shp" %time)
    sea_length = sea_length.drop(['geometry'], axis = 1) #Geometry has no use at the moment.

    #Add chokepoints and pipelines for the corridor into database 
    
    print("------Insert into Corridor Chokepoint-------")
    for key, value in straits.items():
        where_clause = "corridor_name=%s" % repr(key)
        id,_ = get_values(conn, 'corridor','corridor_id', where_clause)
        for ck in value:
            if(ck != 'NONE'):
                where_clause = "strait_name=%s" % repr(ck)
                ck_id,_ = get_values(conn, 'chokepoint', 'chokepoint_id',where_clause)
                id['chokepoint_id'] = ck_id['chokepoint_id']
                insert_into(conn, "corridor_ck", id)

    print("------Insert into Corridor Pipeline-------")
    for key, value in pipe_lines.items():
        where_clause = "corridor_name=%s" % repr(key)
        id,_ = get_values(conn, 'corridor','corridor_id', where_clause)
        for pl in value:
            where_clause = "name=%s" % repr(pl)
            pl_id,_ = get_values(conn, 'pipeline', 'pipeline_id',where_clause)
            id['pipeline_id'] = pl_id['pipeline_id']
            insert_into(conn, "corridor_pipeline", id)
    
    #Insert into seabranch table
    print("------Insert into Corridor Seabranch-------")
    for _, row in sea_length.iterrows():
        where_clause = "corridor_name=%s" % repr(row['corridor_name'])
        id,_ = get_values(conn, 'corridor','corridor_id', where_clause)
        id['country'], id['length'], = [row['country'], row['length']]
        insert_into(conn, 'corridor_seabranch', id)

    #Add the intakes to the table
    alpha_df = alpha_tanker_parser(alphatanker_file)
    
    print("------Insert into Corridor Intake-------")
    for _, row in alpha_df.iterrows():
        corridor_name = row['load_port'] + "-" + row['discharge_port']
        where_clause = "corridor_name=%s" % repr(corridor_name)
        id,_ = get_values(conn, 'corridor','corridor_id', where_clause)
        where_clause = "name=%s" % repr(row['commodity'])
        com_df,_ = get_values(conn,'commodity_lvh','commodity_id',where_clause)
        id['commodity_id'],id['intake'], id['date'], = [com_df['commodity_id'], row['intake'], row['date']]
        insert_corridor_intake(conn, 'corridor_intake', id)

    #LVH does not has the name of alphatanker

flag_test = 0

if(flag_test==1):
    _ ,y = get_values(conn, 'pipeline', where="name='BTC9'")
    print(y)
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    print(time)


close_conn(conn)




