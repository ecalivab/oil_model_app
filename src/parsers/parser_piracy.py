import pandas as pd


def piracy_by_year(input_file, year:int) -> pd.DataFrame:
    piracy = pd.read_excel(input_file)

    new_df = piracy[['Country', 'Piracy and Armed Robbery']]
    new_df.insert(1,'year', year)
    db_colum_names = ['country', 'year', 'piracy']
    new_df.columns = db_colum_names
    return(new_df)

if __name__ == '__main__':
    x = piracy_by_year('../input_data_spreadsheet/2019 Stable Seas Index Data(OEF).xlsx', 2019)
    print(x.head(25))