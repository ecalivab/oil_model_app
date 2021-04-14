import pandas as pd
import numpy as np
def parse_LVH(input_file) -> pd.DataFrame:
    lvh = pd.read_excel(input_file)
    lvh = lvh.drop(['u.m.'], axis=1)
    lvh = lvh.replace('NO', np.nan)
    db_column_name = ['name', 'lvh']
    lvh.columns = db_column_name
    
    return(lvh)

if __name__ == '__main__':
    x = parse_LVH("../input_data_spreadsheet/commodity AT_GDP.xlsx")
    print(x.head(25))