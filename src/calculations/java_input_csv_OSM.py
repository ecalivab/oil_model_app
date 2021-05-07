import sys
import os
sys.path.append(os.getcwd())  

import logging
import pandas as pd
from geopy.geocoders import Nominatim

from parsers.parser_alphatanker import alpha_tanker_parser
from database_driver.database_conn import *

def read_port_coordinate_file(port_file):
    ports = pd.read_excel(port_file)

    return ports

def read_port_country_file(port_file):
    port_country = pd.read_excel(port_file)

    return port_country

def create_input_file(alphatanker_file):

    logging.basicConfig(filename='java_input_cvs_OSM.log', level=logging.DEBUG)

    nom = Nominatim(user_agent="Your_app-name")
    port_country = read_port_country_file("../input_data_spreadsheet/Port_Country.xlsx")
    port_coord = read_port_coordinate_file('../input_data_spreadsheet/coordinatePorti.xls')
    alpha_df = alpha_tanker_parser(alphatanker_file)

    route_port_coord = pd.DataFrame(columns=['RouteName', 'oPort','oCountry', 'olon', 'olat', 'dport', 'dcountry', 'dlon', 'dlat'])

    #Extract Alphatanker Routes
    alpha_df = alpha_df.drop(['commodity','date', 'intake'], axis = 1) #Remove unnessary info
    alpha_df = alpha_df.drop_duplicates() #Remove Duplicates

    cache_ports = {} #Save the ports already looked up

    conn = connect() #Open database connection to know if the corridor already exist

    for _, row in alpha_df.iterrows():
        l_port = row['load_port'] 
        d_port = row['discharge_port']

        not_found_flag = 0

        l_port = l_port.replace("'"," ")  #Some corridors has a ' like N'Kossa that get values cannot process. Replace with a blank space
        d_port = d_port.replace("'"," ")  

        #Get the country of the associated port for better accuracy using Nominatim
        try:
            l_country = port_country[port_country['port']==l_port]['country'].values[0]
        except Exception as e:
            print("Cannot assign load country to port %s: %s" % (l_port ,e))
            logging.warning("Cannot assign load country to port %s: %s" % (l_port ,e))
            continue #Continue with next iteration

        try:   
            d_country = port_country[port_country['port']==d_port]['country'].values[0]
        except Exception as e:
            print("Cannot assign discharge country to port %s: %s" % (d_port, e))
            logging.warning("Cannot assign discharge country to port %s: %s" % (d_port, e))
            d_country = 'Italy' #Now we are focusing in the import of crude of only Italy

        route_name = str(l_port) +"-"+str(d_port)

    
        #Query database for corridor, If corridor doesn't exist it added to the file.
        where_clause = "corridor_name=%s" % repr(route_name)
        _, count = get_values(conn, 'corridor', where=where_clause)

        if (count == 0):
            #The first try will try to find the port 
            #If is not possible it will go to the region name
            #If not possible it will go to the portCoodinate file

            if(l_port in cache_ports.keys()):
                o_lat, o_lon = cache_ports[l_port][0] , cache_ports[l_port][1]
            else:
                try:
                    l_port_aux = l_port + " Port, " + l_country
                    lp_nom = nom.geocode(l_port_aux, timeout=25)
                    o_lat, o_lon = lp_nom.latitude, lp_nom.longitude
                    cache_ports[l_port] = (lp_nom.latitude, lp_nom.longitude)
                except:
                    try:
                        l_port_aux = l_port + ", " + l_country
                        lp_nom = nom.geocode(l_port_aux, timeout=25)
                        o_lat, o_lon = lp_nom.latitude, lp_nom.longitude
                        cache_ports[l_port] = (lp_nom.latitude, lp_nom.longitude)
                    except:
                        try:
                            print(route_name + ' Looked in file')
                            logging.info(route_name + ' Looked in file')
                            o_lat = port_coord[port_coord['port']==l_port]['lat'].values[0]
                            o_lon = port_coord[port_coord['port']==l_port]['long'].values[0]
                            cache_ports[l_port] = (o_lat, o_lon)
                        except:
                            print("Port Not Found in Port Coordinates File: " + str(l_port))
                            logging.warning("Port Not Found in Port Coordinates File: " + str(l_port))
                            not_found_flag = 1
            
            if(d_port in cache_ports.keys()):
                d_lat, d_lon = cache_ports[d_port][0] , cache_ports[d_port][1]
            else:
                try:
                    d_port_aux = d_port + "Port, " + d_country
                    dp_nom = nom.geocode(d_port_aux, timeout=25)
                    d_lat, d_lon = dp_nom.latitude, dp_nom.longitude
                    cache_ports[d_port] = (dp_nom.latitude, dp_nom.longitude)
                except:
                    try:
                        d_port_aux = d_port + ", " + d_country
                        dp_nom = nom.geocode(d_port_aux, timeout=25)
                        d_lat, d_lon = dp_nom.latitude, dp_nom.longitude
                        cache_ports[d_port] = (dp_nom.latitude, dp_nom.longitude)
                    except:
                        try:
                            print(route_name + ' Looked in file')
                            logging.info(route_name + ' Looked in file')
                            d_lat = port_coord[port_coord['port'] == d_port]['lat'].values[0]
                            d_lon = port_coord[port_coord['port'] == d_port]['long'].values[0]
                            cache_ports[d_port] = (d_lat, d_lon)
                        except:
                            print("Port Not Found in Port Coordinates File: " + str(d_port))
                            logging.warning("Port Not Found in Port Coordinates File: " + str(d_port))
                            not_found_flag = 1

            
            if(not_found_flag == 0):
                row = {'RouteName': route_name, 'oPort': l_port,'oCountry': l_country ,'olon': o_lon,'olat': o_lat,
                'dport':d_port, 'dcountry':d_country, 'dlon': d_lon, 'dlat': d_lat}
                route_port_coord = route_port_coord.append(row, ignore_index=True)
            else:
                not_found_flag = 0

    route_port_coord.to_csv('java_input.csv',index=False) #Need to add output Directory 

    close_conn(conn)

def prepare_java_file(java_csv) -> pd.DataFrame:

    conn = connect()

    routes_df = pd.read_csv(java_csv)
    routes_df = routes_df.drop(['olon','olat', 'dlon', 'dlat'], axis = 1) #Remove unnessary info
    pipeline_dict = {}
    db_column_names = ['corridor_name', 'load_port', 'load_country', 'discharge_port','discharge_country']

    routes_df.columns = db_column_names

    for _, row in routes_df.iterrows():

        l_port = row['load_port']
        l_country = row['load_country']

        where_clause = "load_port=%s" % repr(l_port) 
        
        pipeline, count = get_values(conn, 'pipeline', 'name', where_clause)
        #Check if the pipeline by port exist save it otherwise look for the country.
        if(count == 0):
            where_clause = "load_port=%s" % repr(l_country) 
            pipeline, count = get_values(conn, 'pipeline', 'name', where_clause)
            pipeline_dict[row['corridor_name']] = pipeline['name'].tolist()
        else:
            pipeline_dict[row['corridor_name']] = pipeline['name'].tolist()

    close_conn(conn)

    return routes_df, pipeline_dict

if __name__ == '__main__':
    #create_input_file('../input_data_spreadsheet/4_export_prova_alph_2.xlsx')
    create_input_file('../input_data_spreadsheet/alphatanker_files/2019/01_01-31_03 alphatanker.xlsx')
    df, pipe_dict = prepare_java_file('java_input.csv')
    print(df.head(60))

    for key, value in pipe_dict.items():
        print(key, value)

    '''
    conn = connect()
    corridor_name = "N'Kossa Terminal-Leghorn"
    corridor_name = corridor_name.replace("'"," ")
    where_clause = "corridor_name=%s" % repr(corridor_name)
    _, count = get_values(conn, 'corridor', where=where_clause)
    print(count)
    close_conn(conn)
    '''

    
    