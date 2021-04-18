import sys
import os
sys.path.append(os.getcwd())  

from numpy.core.numeric import NaN
import pandas as pd
from database_driver.database_conn import *
import math


############################################## GEO RISK ###########################################################

def geo_risk (conn, year) -> pd.DataFrame:
    #Query Database with the selected year
    where_clause = "year=%s" % repr(year)
    wgi_df, _ = get_values(conn, 'wgi', where=where_clause)
    piracy_df, _ = get_values(conn, 'piracy_index', where=where_clause)
    print(wgi_df)
    #Sea Risk
    wgi_piracy = pd.merge(wgi_df,piracy_df,on=['country','year'],how="outer",indicator=True) #Outer join because not all the contries are in the piracy file.
    wgi_piracy['piracy'] = wgi_piracy['piracy'].replace(NaN, 100)
    #GeoRisk
    
    wgi_piracy["geo_risk"] = wgi_piracy.iloc[:,2:8].sum(axis=1).div(6)
    wgi_piracy["sea_risk"] = wgi_piracy.iloc[:,2:9].sum(axis=1).div(7)
  
    wgi_piracy["geo_risk"] = wgi_piracy["geo_risk"].map(lambda x: 100 -x)
    wgi_piracy["sea_risk"] = wgi_piracy["sea_risk"].map(lambda x: 100 -x)


    wgi_piracy.drop(wgi_piracy.columns[2:10],axis=1,inplace=True)

    #Open Sea Risk
    row = {'country':'Open sea', 'year':year, 'geo_risk': wgi_piracy["geo_risk"].mean(), 'sea_risk':wgi_piracy["sea_risk"].mean()}
    wgi_piracy=wgi_piracy.append(row, ignore_index=True)

    return wgi_piracy

######################################## CHOKEPOINT RISK ###########################################################

def normalization(a, max_val, min_val):
    return ((math.log(a+1) - math.log(min_val+1))/(math.log(max_val+1) - math.log(min_val+1)))


def alpha_normalized(conn):
    chokepoint_df,_ = get_values(conn, 'chokepoint') 
    #min_value = chokepoint_df['alpha'].min()
    min_value = 4 #For now the lowest value is 4 since the table need to be update with updated values
    max_value = chokepoint_df['alpha'].max()

    chokepoint_df['alpha_normalized'] = chokepoint_df['alpha'].map(lambda a: normalization(a, max_value, min_value))

    return chokepoint_df

def chokepoint_risk(conn, year):
    where_clause = "year=%s" % repr(year)
    geo_risk_df,_ = get_values(conn,'geo_risk',where=where_clause)
    chokepoints_df = alpha_normalized(conn)
   
    ck_risk_df = pd.DataFrame(columns=['strait_name', 'chokepoint_risk', 'year'])
    for _, row in chokepoints_df.iterrows():
        strait_id = row['chokepoint_id']
        norm_alpha = row['alpha_normalized']
        name = row['strait_name']
        where_clause = "chokepoint_id=%s" % repr(strait_id)
        country,count = get_values(conn, 'country_chokepoint', where=where_clause) 
        geo_risk_country = pd.merge(geo_risk_df,country,on=['country'],how="inner",indicator=True)
        try:
            compound_risk = (((geo_risk_country['sea_risk'].sum())/count)*norm_alpha)*0.01
            new_row = {'strait_name': name, 'chokepoint_risk': compound_risk, 'year': year }
            ck_risk_df = ck_risk_df.append(new_row, ignore_index=True)
        except ZeroDivisionError as err:
            print("%s, Check is geo_risk table is populated" % err)
              
    return(ck_risk_df)


#For every corridor I need to calculate the risk "1-(sea_risk*relative_length)" for sea "1 -(geo_risk * relative_length)" "
#Problem: How to trigger it -> Trigger, use java_input_file -> by row?
#Instead of using the java_input maybe a temporary table can be better

def product(type, weight, geo_risk, sea_risk):
    if type == 'sea':
        return (1- (weight*sea_risk*0.01))
    elif type == 'captive':
        return(1 - (weight*geo_risk*0.01))
    else:
        return (NaN)

def corridor_failure(conn, java_input_csv, year): 
    #Calculate risk for crude and for the other commodities
    corridor = pd.read_csv(java_input_csv)
    #Getting the Geo_risk by year!!!
    where_clause = "year=%s" % repr(year)
    geo_risk,_ = get_values(conn,'geo_risk',where=where_clause)


    for _, row in corridor.iterrows():
        corridor_failure = pd.DataFrame(columns=['corridor_id','pipeline_id','corridor_failure_captive','corridor_failure_no_captive'])
        #WEIGHTS!!!
        corridor_name = row['RouteName']
        id = get_values_simple(conn,'corridor',['corridor_id'],'corridor_name=%s' % corridor_name)
        corridor_id =id['corridor_id'].values[0]
        #Just Sea without Captive
        sea_branch = get_values_simple(conn, 'corridor_seabranch', where='corridor_id=%s' % corridor_id)
        sea_branch['type'] = 'sea'
        total_length = sea_branch['length'].sum()
        sea_branch['weight_without_captive'] = sea_branch['length'].div(total_length)

        #Calculate CK Risk
        #Find Chokepoints in the route.
        ck, count = get_values(conn, 'corridor_ck', where="corridor_id=%s" % repr(corridor_id))
        ck_risk = 1

        if count == 0:
            ck_risk = 0
        else:
            for _, row in ck.iterrows():
                ck_id = row['chokepoint_id']
                strait_name = get_values_simple(conn, 'chokepoint', ['strait_name'], where="chokepoint_id=%s" % ck_id)
                strait_name = strait_name['strait_name'].values[0]
                ck_risk_aux = get_values_simple(conn, 'chokepoint_risk', ['chokepoint_risk'], where="strait_name=%s" % strait_name)
                ck_risk_aux = ck_risk_aux['chokepoint_risk'].values[0]
                ck_risk = (1 - ck_risk_aux) * ck_risk

        #Adding Captive
        pipeline_id = get_values_simple(conn, 'corridor_pipeline', ['pipeline_id'], where="corridor_id=%s" % corridor_id) 
        
        for _, pipe in pipeline_id.iterrows(): #If some country has more than one pipeline
            pipeline_id = pipe['pipeline_id']
            captive_branch = get_values_simple(conn, 'country_pipeline', ['pipeline_id', 'country', 'length'], where="pipeline_id=%s" %pipeline_id)
            captive_branch['corridor_id'],captive_branch['type'] = [corridor_id,'captive']
            captive_branch = captive_branch.reset_index(drop=True)
            weights = pd.concat([sea_branch, captive_branch], axis=0)
            total_length = weights['length'].sum()
            weights['weight_with_captive'] = weights['length'].div(total_length)
            weights = weights.drop(columns=['corridor_seabranch_id', 'length'])
            #PRODUCTORIA
            risk = pd.merge(weights,geo_risk,on='country')
            risk['productoria_without_captive'] = risk.apply(lambda row: product(row['type'], row['weight_without_captive'],row['geo_risk'], row['sea_risk']), axis=1)
            risk['productoria_captive'] = risk.apply(lambda row: product(row['type'], row['weight_with_captive'],row['geo_risk'], row['sea_risk']), axis=1)

            #Calculate final risk
            produtoria_captive = risk['productoria_captive'].product()
            produtoria_no_captive = risk['productoria_without_captive'].product()

            result_captive = (1-produtoria_captive) * ck_risk
            result_no_captive = (1-produtoria_no_captive) * ck_risk
            
            new_row = {'corridor_id': corridor_id, 'pipeline_id':pipeline_id  ,'corridor_failure_captive': result_captive, 'corridor_failure_no_captive': result_no_captive}
            corridor_failure = corridor_failure.append(new_row, ignore_index=True)
        
        print(corridor_failure)
        #insert_into(conn, 'corridor_failure', corridor_failure)

    return


def risk_single_corridor (conn, route_name ,commodity, start_date, end_date=None): #The Pipeline ID should be pass as argument so the user can choose which route wants
    corridor_id = get_values_simple(conn, 'corridor', ['corridor_id'], where="corridor_name=%s" % route_name)
    corridor_id = corridor_id['corridor_id'].values[0]
    
    commodity_df = get_values_simple(conn, 'commodity_lvh', where="name=%s" % commodity)
    commodity_id = commodity_df['commodity_id'].values[0]
    lvh = commodity_df['lvh'].values[0]

    pipeline_share = 1
    
    if(commodity=='Heat Crude' or commodity=='Crude Condensates' or commodity=='Non Heat Crude'):
        pipeline_id = get_values_simple(conn, 'corridor_pipeline', ['pipeline_id'], where="corridor_id=%s" % corridor_id)
        pipeline_id = pipeline_id['pipeline_id'].values[0]
        pipeline_share = get_values_simple(conn, 'pipeline', ['share_val'], where="pipeline_id=%s" % pipeline_id)
        pipeline_share = pipeline_share['share_val'].values[0]
        corridor_failure = get_values_simple(conn, 'corridor_failure',['corridor_failure_captive'],where="corridor_id=%s" % corridor_id) 
        corridor_failure = corridor_failure['corridor_failure_captive'].values[0]
    else:
        corridor_failure = get_values(conn, 'corridor_failure',['corridor_failure_no_captive'],where="corridor_id=%s" % corridor_id) 
        corridor_failure = corridor_failure['corridor_failure_no_captive'].values[0]

    if (end_date is not None):
        where_clause = "(commodity_id=%s AND corridor_id=%s AND date>=%s AND date<= %s)" % (repr(commodity_id),repr(corridor_id), repr(start_date), repr(end_date))
        intake,_ = get_values(conn, 'intake', 'SUM(intake)', where=where_clause)
    else:
        where_clause = "(commodity_id=%s AND corridor_id=%s AND date>=%s)" % (repr(commodity_id),repr(corridor_id), repr(start_date))
        intake,_ = get_values(conn, 'corridor_intake', 'SUM(intake) AS intake', where=where_clause)

    total_intake = intake['intake'].values[0]

    corridor_energy = total_intake*pipeline_share*lvh*0.2778 #LVH in MJ
    #corridor_energy = total_intake*pipeline_share*lvh #LVH in MWh
    final_risk = corridor_energy*corridor_failure

    print(final_risk)

    return final_risk

def risk_corridor(conn, country ,commodity, start_date, end_date=None):
    corridors,_ = get_values(conn, "corridor","route_name",where="load_country=%s" % repr(country)) 
    
    for _, row in corridors.iterrows():
        single_risk = risk_single_corridor (conn, row['route_name'] ,commodity, start_date, end_date)
        total_risk =+ single_risk

    return total_risk

if __name__ == '__main__':

    connection = connect()
        
    geo_risk_df = geo_risk(connection,'2019')
    print(geo_risk_df)
    print(geo_risk_df[geo_risk_df['country']=='Open sea'])
    print(geo_risk_df[geo_risk_df['country']=='Egypt, Arab Rep.'])
    #insert_into(connection, 'geo_risk', geo_risk_df)
    #x = chokepoint_risk(connection, '2019')
    #print(x.head(50))
    #insert_into(connection,'chokepoint_risk',x)
    #corridor_failure(connection,'java_input.csv', '2019')
    #risk_single_corridor(connection,'Ceyhan-Trieste','Non Heat Crude', '2020-09-15')
    
    ###### TEST SANITATION STRINGS IN QUERYS########################
    '''
    where_clause = "corridor_name=%s" % 'Alexandria-Augusta'
    compound_query = "pipeline_id=(SELECT pipeline_id FROM corridor_pipeline WHERE corridor_id=%s)" % '46'
    #; SELECT * FROM corridor;
    #print(compound_query)
    #
    #,['corridor_id', 'corridor_name'] 
    id = get_values_simple(connection,'corridor',where=where_clause)
    
    print(id)
    '''
    close_conn(connection)
 