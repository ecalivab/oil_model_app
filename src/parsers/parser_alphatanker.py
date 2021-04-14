import pandas as pd
import numpy as np
import re

def alpha_tanker_parser(alpha_file) -> pd.DataFrame: 
    at_data = pd.read_excel(alpha_file,header=[1,2,3], skipfooter=1)  #Skipfooter =1 is use to remove the Grand Total row at the end.
    at_data = at_data.drop(at_data.filter(regex='Total').columns, axis=1) #Clean the column Total that is not of our interest

    #Create a new Dataframe to add our expanded multiheader into a single header prepared for the database.
    clean_alpha_df  = pd.DataFrame(columns=["load_port", "discharge_port", "commodity", "date", "intake"])


    load_port = list(at_data['Load Port', 'Unnamed: 0_level_1', 'Unnamed: 0_level_2'])


    for port in load_port:
        new_df = at_data[at_data['Load Port', 'Unnamed: 0_level_1', 'Unnamed: 0_level_2'] == port] #Create a temporal dataframe with only one row value (port)
        new_df = new_df.dropna(axis='columns') #Remove the NaN entrances by row 
        for column in new_df.columns:
            if(column[0] != "Load Port"):
                intake = new_df[column].values #Get Intake value from multi-index header
                port = re.sub(r'\([^)]*\)', '', port).strip()
                d_port = re.sub(r'\([^)]*\)', '', column[0]).strip()
                new_row = {'load_port': port, 'discharge_port':d_port, 'commodity':column[1], 'date': column[2], 'intake': intake[0]}
                clean_alpha_df = clean_alpha_df.append(new_row, ignore_index=True)

    return clean_alpha_df



if __name__ == '__main__':
    alpha_tanker_df = alpha_tanker_parser('../input_data_spreadsheet/4_export_prova_alph.xlsx')
    
    print(alpha_tanker_df.head(100))




#FOR TESTING
'''
new_df = at_data[at_data['Load Port', 'Unnamed: 0_level_1', 'Unnamed: 0_level_2'] == load_port[15]]
new_df = new_df.dropna(axis='columns')
print(new_df)
print("----------------------------------------------------------------------------------------------------------------------")
print(new_df.columns[1])
x = new_df.columns[1]
print(new_df[x].values)
'''