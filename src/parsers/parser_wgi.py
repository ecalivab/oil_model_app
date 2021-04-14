import pandas as pd
from functools import reduce



def prepare_wgi(wgi_file):
    #This spreadsheet has a diferent sheets and has a multipleheader, we need to parse each spreadsheet individually. 
    wgi_dataset = pd.ExcelFile(wgi_file) 
    sheets = wgi_dataset.sheet_names
    #Each sheet is a multiheader with the year and the a calculation our interest is to parse the rank. 
    #The idea is to have Country Year Indicator1 Indicator2 Indicator3 ...
    #First we are going to create a diferent dataframe for each indicator and then combine everything for Country and Year
    del(sheets[0]) #Remove Introduction Sheet
    return wgi_dataset, sheets

#Parsing sheet by sheet

def wgi_first_time(wgi_file)-> pd.DataFrame:
    wgi_dataset, sheets = prepare_wgi(wgi_file)

    df_list = []

    for s in sheets:
        tmp_df = pd.DataFrame(columns=['Country', 'Year', s]) #Temporary data frame 
        df = wgi_dataset.parse(sheet_name=s, header=[13,14]) #Take the headers for year and calculations (Estimate	StdErr	NumSrc	Rank	Lower	Upper)
        
        list_columns = [x for x in df.columns if 'Rank' in x]  #Take the values of columns that have Rank in it 

        for c in list_columns: #Need to cycle over every row to get the row for the new dataframe 
            for row in zip(df['Unnamed: 0_level_0', 'Country/Territory'],df[c]):
                new_row = {'Country': row[0], 'Year': c[0], s: row[1]}
                tmp_df = tmp_df.append(new_row, ignore_index=True)
        df_list.append(tmp_df)

    wgi_clead_df = reduce(lambda left,right: pd.merge(left,right,on=['Country', 'Year']), df_list)
    return wgi_clead_df

def wgi_by_year(wgi_file, year:int) -> pd.DataFrame:
    wgi_dataset, sheets = prepare_wgi(wgi_file)

    df_list = []

    for s in sheets:
        tmp_df = pd.DataFrame(columns=['Country', 'Year', s])
        df = wgi_dataset.parse(sheet_name=s, header=[13,14])
        
        for row in zip(df['Unnamed: 0_level_0', 'Country/Territory'],df[year, 'Rank']):
            new_row = {'Country': row[0], 'Year': year, s: row[1]}
            tmp_df = tmp_df.append(new_row, ignore_index=True)

        df_list.append(tmp_df)

    wgi_clead_df = reduce(lambda left,right: pd.merge(left,right,on=['Country', 'Year']), df_list)
    db_colum_names = ['country', 'year','voice_accountability','political_stability', 'gov_effectiviness','regulatory_quality','rule_of_law', 'control_of_corruption']
    
    wgi_clead_df.columns = db_colum_names

    return wgi_clead_df


if __name__ == '__main__':
    x = wgi_by_year("../input_data_spreadsheet/wgidataset.xlsx",2000)
    #y = wgi_first_time("../input_data_spreadsheet/wgidataset.xlsx")
    print(x.head(80))
    
#df.drop(labels='Rank', axis=1, level=1, inplace=True) #drop a column in a multiheader problem
#df = df[[x for x in df.columns if 'Rank' in x]] #Filter column in a multiheader   
    
    