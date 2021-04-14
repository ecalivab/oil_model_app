import pandas as pd
import geopandas as gpd
from pygeos.measurement import length
from shapely.geometry import Point
import matplotlib.pyplot as plt


#Read the EEZ file version 11 and the route shapefile taken from the eurostat/searoute
#and converts them in GeoDataFrame

def shape_file_read(route_shp) -> gpd.GeoDataFrame: #Route shp is the only one changing the other ones doesn't change often
    print("-----Reading the EEZ shapefile------")
    eez = gpd.read_file("shape_files/EEZ_shp/eez_v11.shp")

    print("-----Reading the Route shapefile------")
    route = gpd.read_file(route_shp)

    print("-----Reading the Straits shapefile------")
    straits = gpd.read_file("shape_files/straits_shp_ed/STRAIT_ED.shp")

    print("-----End Reading Files------")

    return eez, route, straits

def compute_routes_length(route_shp):
    eez, route, straits = shape_file_read(route_shp)

    #Variables
    sovereignCountryPerRoute = {}
    route_length_df = pd.DataFrame()
    routeStraits = {}
    route['straits'] = '' #Adding to route a new value of straits to add entra information to the route

    #Convert the LINESTRING to POINTS
    #  1) Take the coordinates of the Line
    #  2) Create a new Data Frame
    #  3) Add the name of the route to the DF 
    #  4) Apply a transformation to obtain a Point Object
    #  5) Transform DataFrame to GeoDataFrame 


    #The first routine will return the Soverign countries the route cross
    #this to prevent doing an overlay with the whole eez since is a expensive operation
    #It is possible to intersect a point in a polygon with sjoin (spatial join)
    #First we will extact the coordinates of the linestring a create a new dataframe
    #then we will apply to the dataframe a function that goes row by row taking the lat and long
    #and adding with Point() then we use sjoin to get the eez zone where this point intersect
    #Then we take each value of the eez 

    print("-----Start of the route to point convertion------")

    for row in range(len(route)):
        x= list(route.geometry[row].coords)
        df = pd.DataFrame(x, columns=['long', 'lat'])
        route_name = route['RouteName'][row]
        points = df.apply(lambda rowL: Point(rowL.long, rowL.lat), axis=1)
        route_point = gpd.GeoDataFrame(df, geometry=points) #New GeoFrame with the route decomposed in points.
        route_point.set_crs(eez.crs, inplace=True)  #Set CRSthe new GeoDataFrame this case same as eez.
        print("-----Intersecting points with EEZ Zone------"+ str(route_name))
        route_ezz = gpd.sjoin(route_point,eez, how='inner', op='intersects') #Intersect the points of the route with the eez zones so we know which economics zones are crossed.
        print("-----Intersecting points with Straits------")
        route_ck = gpd.sjoin(route_point,straits, how='inner', op='intersects') #Intersect the straits.
        crossed_countries = route_ezz["SOVEREIGN1"].unique()
        crossed_straits = ["NONE"]
        if (route_ck['SUB_REGION'].unique().size != 0):
            crossed_straits = route_ck['SUB_REGION'].unique()
        sovereignCountryPerRoute[route_name] = crossed_countries
        routeStraits[route_name] = crossed_straits #Add to dictionary
        route.loc[route['RouteName'] == route_name,'straits'] = pd.Series([crossed_straits]) #loc added to clean SettingWithCopyWarning

    print("-----End the route to point convertion------")

    #This method goes through each route with the pre-calculated crossed soverign countries
    #Take one route at the time and calculate the legth of the line that intersect the eez polygon
    #with the overlay function, then it calculates the lenght of the route for each eez zone 
    #finally creates a new dataframe with the route name - country - length

    print("-----Start of route length calculations------")

    for route_l, country_list in sovereignCountryPerRoute.items():
        
        one_route = gpd.GeoDataFrame(route[route['RouteName'] == route_l])
        one_route.set_crs(eez.crs, inplace=True)
        
        interested_eez = gpd.GeoDataFrame(eez[eez['SOVEREIGN1'].isin(country_list)])
        interested_eez.set_crs(eez.crs, inplace=True)
        print("-----Starting intersection of route " + route_l + "------")
        route_eez_intersect = gpd.overlay(one_route,interested_eez, how='intersection')
        print("-----End of intersection of route " + "------")

        route_eez_intersect.to_crs(epsg=3857, inplace=True)  #pseudo mercator projection
        route_eez_intersect['length'] = route_eez_intersect['geometry'].length/1000

        #Calculate how long is the route for finding the difference with International Waters.
        one_route.to_crs(epsg=3857, inplace=True) #pseudo mercator
        total_length = one_route['geometry'].length/1000

        suma = route_eez_intersect['length'].sum()
        international_waters = total_length.values[0]-suma
        
        route_eez_intersect = route_eez_intersect[route_eez_intersect['SOVEREIGN1']!= 'Italy'] #At the moment we only care about discharge country Italy we don't take it into consideration.

        final_df = route_eez_intersect[['RouteName','SOVEREIGN1','length','geometry']].dropna()
        if(international_waters >= 200):
            row = {'RouteName': route_l,'SOVEREIGN1': 'Open sea','length': international_waters, 'geometry': 'NONE'}
            final_df = final_df.append(row, ignore_index=True)

        route_length_df = route_length_df.append(final_df, ignore_index = True) 
        

    print("-----End the route to point convertion------")

    db_column_names = ['corridor_name','country', 'length', 'geometry']
    route_length_df.columns = db_column_names

    return route_length_df, routeStraits

if __name__ == '__main__':
    route_length, straits = compute_routes_length("./shape_files/new_route_test/out.shp")
    
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    print(route_length.head(50))

    
    
    print("Crossed Straits")
    for key, value in straits.items():
        print(key + ": " + str(value))


    #route_length.to_csv('debug_intersection.csv',index=False)
    