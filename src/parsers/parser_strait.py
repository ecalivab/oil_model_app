import pandas as pd

def parse_strait(input_file) -> pd.DataFrame:
    straits_country = pd.read_excel(input_file)

    straits_name_df = straits_country[['strait_name', 'alpha']] #Double brackets to return a dataframe other wise return a series
    straits_country = straits_country.drop(columns='alpha')
    dict_straits = straits_country.set_index('strait_name').T.to_dict('list')
    

    
    
    return straits_name_df, dict_straits


if __name__ == '__main__':
    df, dict_strait = parse_strait('../input_data_spreadsheet/straits_country.xlsx')
    print(df)

    for key, value in dict_strait.items():
        print(key + '->' + str(value))