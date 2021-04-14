import pandas as pd

def parse_pipeline(input_file) -> pd.DataFrame:
    pipe_lines = pd.ExcelFile(input_file)
    df = pipe_lines.parse(sheet_name='pipeline _characteristic')
    return df

def parse_pipeline_country(input_file) -> pd.DataFrame:
    pipe_lines = pd.ExcelFile(input_file)
    df = pipe_lines.parse(sheet_name='pipeline_countries')
    return df

def parse_surface(input_file) -> pd.DataFrame:
    pipe_lines = pd.read_excel(input_file)
    return pipe_lines

if __name__ == '__main__':
    df = parse_pipeline_country('../input_data_spreadsheet/pipeline_info.xlsx')
    print(df)
    df = parse_surface('../input_data_spreadsheet/surface_area_country.xls')
    print(df)
