from os import execle
import pandas as pd
import numpy as np
from stories.models import CorridorIntake, Corridor, CommodityLvh , CorridorFailure, Pipeline
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from datetime import datetime



def common_querys(year, crude_flag):
    if crude_flag == 1:
        df_corridor = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','load_country','discharge_port','load_port'))
        df_intake =   pd.DataFrame.from_records(
            CorridorIntake.objects.filter(Q(date__year=year), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','commodity','date'))
        intake_df_previous = pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year = int(year)-1), Q(commodity=66)|Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','commodity','date'))

        return df_corridor, df_intake, intake_df_previous

def total_intake_variable(start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    start_date_last = start_date - relativedelta(years=1)
    end_date_last = end_date - relativedelta(years=1)
    start_date_last = datetime.strftime(start_date_last, '%Y-%m-%d')
    end_date_last = datetime.strftime(end_date_last, '%Y-%m-%d')

    intake_df =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__lte=end_date), Q(date__gte=start_date), Q(commodity=66)|Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))
    intake_df_last =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__lte=end_date_last), Q(date__gte=start_date_last), Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))


    if intake_df.empty or intake_df_last.empty:
        total_intake = 0
        total_intake_last = 0
    else:
        total_intake = intake_df['intake'].sum()
        total_intake_last = intake_df_last['intake'].sum()

    variation = ((total_intake - total_intake_last) / total_intake_last) * 100
    
    return total_intake, variation


def fix_time_format(daterange):
    daterange = daterange.split("-")
    end_date = daterange[1].strip()
    current_date = end_date
    end_date = datetime.strptime(end_date, '%m/%d/%Y')
    start_date = daterange[0].strip()
    first_date= start_date
    start_date = datetime.strptime(start_date, '%m/%d/%Y')
    end_date = end_date.strftime('%Y-%m-%d')
    start_date = start_date.strftime('%Y-%m-%d')

    return start_date, end_date, current_date, first_date


def get_port_max_intake(start_date, end_date):
    intake_df =   pd.DataFrame.from_records(
     CorridorIntake.objects.filter(Q(date__lte=end_date), Q(date__gte=start_date), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))
    corridor_df = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','discharge_port'))

    intake_df.columns = ['corridor_id', 'intake', 'date']
    df = pd.merge(corridor_df,intake_df,on=['corridor_id'],how="outer",indicator=True)
    df =df.drop(['corridor_id'], axis = 1)
    df = df.groupby(['discharge_port']).sum().reset_index()
    df = df.nlargest(5,'intake')
    df.columns = ['Port','Intake [MTons]']
    return df

def intake_variation_year(intake_df, intake_previous_df):

    total_intake = (intake_df['intake'].sum())

    if intake_previous_df.empty:
        variation = "No Data Available"
    else:
        total_intake_last = intake_previous_df['intake'].sum()
        variation = round((((total_intake - total_intake_last) / total_intake_last) * 100),2)
    
    total_intake = round(total_intake/1000000,2)

    return total_intake, variation

def load_country_intake_stats(df_corridor, df_intake):
    df_intake = df_intake.drop(['commodity'], axis= 1)
    df_intake.columns = ['corridor_id', 'intake', 'date']

    df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
    df =df.drop(['corridor_id', 'discharge_port'], axis = 1)
    df = df.groupby(['load_country']).sum().reset_index()
    df = df[df['intake']> 0] # filter values that are more than zero
    total_sum = df['intake'].sum()
    df['percentage'] = df['intake'].apply(lambda x: round((x/total_sum)*100,2))

    return df

def top_five_load_countries(df):
    top_five_df = df.nlargest(5,'intake')
    top_five_df['intake'] =  df['intake'].apply(lambda x: round((x/1000000),2))

    top_five = top_five_df.drop(['intake'], axis = 1)
    top_five_dic = pd.Series(top_five.percentage.values,index=top_five.load_country).to_dict()

    top_five_df.columns = ['Port','Intake [MTons]', 'Percentage [%]']

  
    return top_five_dic, top_five_df

def side_bar_data_crude(corridor_id,year, percentage_df):
    corridor = Corridor.objects.filter(corridor_id=corridor_id).values()

    #Point 1
    try:
        percentage = percentage_df['percentage'][percentage_df['load_country']==corridor[0].get('load_country')].values[0]
        intake = percentage_df['intake'][percentage_df['load_country']==corridor[0].get('load_country')].values[0]
    except:
        percentage = 0
        intake = 0
    
    
    ports =  pd.DataFrame.from_records(Corridor.objects.filter(load_country = corridor[0].get('load_country')).values('corridor_id','load_port', 'discharge_port'))
    ports.columns = ['corridor','load_port', 'discharge_port']

    df_intake =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year=year), Q(commodity=66)|Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake'))

    intake_df_last = pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year = int(year)-1), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake'))

    if intake_df_last.empty:
        variation = "No Data Available"
    else:
        df2 = pd.merge(ports, intake_df_last, on=['corridor'],how="outer")
        total_intake_last = df2['intake'].sum()
        variation = round((((intake - total_intake_last) / total_intake_last) * 100),2)
    
    df = pd.merge(ports, df_intake, on=['corridor'],how="outer")
    df =df.drop(['corridor','discharge_port'], axis = 1)
    df = df.groupby(['load_port']).sum().reset_index()
    df = df[df['intake']> 0] 
    top_three = df.nlargest(3,'intake')
    top_three_dict = pd.Series(top_three.intake.values,index=top_three.load_port).to_dict()

   
    country_dict = {'percentage': percentage, 'intake': intake, 'variation': variation, 'top_three': top_three_dict}

    #Point2
    total_sum = df['intake'].sum()
    df['percentage'] = df['intake'].apply(lambda x: round((x/total_sum),2)*100)

    try:
        load_port_intake = df['intake'][df['load_port']==corridor[0].get('load_port')].values[0]
        load_port_percentage = df['percentage'][df['load_port']==corridor[0].get('load_port')].values[0]
    except:
        load_port_intake = 0
        load_port_percentage = 0
   

    if intake_df_last.empty:
        load_port_variation = "No Data Available"
    else:
        df2_l =df2.drop(['corridor','discharge_port'], axis = 1)
        df2_l = df2_l.groupby(['load_port']).sum().reset_index()
        load_port_intake_last = df2_l['intake'][df2_l['load_port']== corridor[0].get('load_port')].values[0]
        load_port_variation = round((((load_port_intake - load_port_intake_last) / load_port_intake_last) * 100),2)

    load_dict = {'intake': load_port_intake, 'percentage': load_port_percentage, 'variation': load_port_variation}

    #Point3

    df_discharge = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','discharge_port'))
    df_discharge.columns = ['corridor', 'discharge_port']
    df_discharge = pd.merge(df_discharge,df_intake,on=['corridor'],how="outer",indicator=True)
    df_discharge =df_discharge.drop(['corridor'], axis = 1)
    df_discharge = df_discharge.groupby(['discharge_port']).sum().reset_index()

    try:
        total_discharge_port_intake = df_discharge['intake'][df_discharge['discharge_port']==corridor[0].get('discharge_port')].values[0]   
    except:
         total_discharge_port_intake = 0

    df_dp = pd.merge(ports, df_intake, on=['corridor'],how="outer")
    df_dp = df_dp.drop(['corridor','load_port'], axis = 1)
    df_dp = df_dp.groupby(['discharge_port']).sum().reset_index()
    df_dp = df_dp[df_dp['intake']> 0] 

    total_sum_dp = df_dp['intake'].sum()
    df_dp['percentage'] = df_dp['intake'].apply(lambda x: round((x/total_sum_dp),2)*100)

    try:
        discharge_port_intake = df_dp['intake'][df_dp['discharge_port']==corridor[0].get('discharge_port')].values[0]
        discharge_percentage = df_dp['percentage'][df_dp['discharge_port']==corridor[0].get('discharge_port')].values[0]
    except:
        discharge_port_intake = 0
        discharge_percentage = 0
    

    if intake_df_last.empty:
        discharge_port_variation = "No Data Available"
    else:
        df3 =df2.drop(['corridor','load_port'], axis = 1)
        df3 = df3.groupby(['discharge_port']).sum().reset_index()
        discharge_port_intake_last = df3['intake'][df3['discharge_port']== corridor[0].get('discharge_port')].values[0]
        discharge_port_variation = (((discharge_port_intake - discharge_port_intake_last) / discharge_port_intake_last) * 100).round(4)


    dicharge_dict = {'total_intake': total_discharge_port_intake,'intake': discharge_port_intake, 'percentage': discharge_percentage, 'variation': discharge_port_variation}

    return country_dict, load_dict, dicharge_dict
    

def risk_side_bar_crude(pipeline_id, corridor_id, year):
    risk = 0.0

    intake_df = pd.DataFrame.from_records(CorridorIntake.objects.filter(Q(commodity=66)|Q(commodity=54)|Q(commodity=22)|Q(commodity=77), date__year=year, corridor = corridor_id).values('corridor','commodity','intake'))
    failure = CorridorFailure.objects.values_list('corridor_failure_captive', flat=True).get(corridor = corridor_id, year=2019, pipeline = pipeline_id)
    pipeline = Pipeline.objects.values_list('share_val','name','total_length').get(pipeline_id =pipeline_id)
    

    if intake_df.empty == False:
        intake_df = intake_df.groupby(['corridor','commodity']).agg({'intake': 'sum',}).reset_index()
        corridor_intake = intake_df['intake'].sum()

        for _, row_i in intake_df.iterrows():
            lvh = CommodityLvh.objects.values_list('lvh', flat=True).get(commodity_id = row_i['commodity'])
            risk = risk + row_i['intake']*pipeline[0]*failure*lvh*0.2778
    else:
        corridor_intake = 0

    corridor_dict = {'risk':round(risk, 2), 'corridor_intake': corridor_intake, 'pipeline_name': pipeline[1],'length': pipeline[2]}
    
    return corridor_dict

def percentual_var(intake_current, intake_previous):
    try:
        variation = round(((intake_current/intake_previous) - 1)*100,2)
    except:
        variation = np.nan
    return variation

def table_with_variations(df_corridor, df_intake, df_intake_previous, year):

    intake_df = df_intake.drop(['commodity', 'date'], axis= 1)
    intake_df.columns = ['corridor_id', 'intake']
    df = pd.merge(df_corridor,intake_df,on=['corridor_id'],how="outer",indicator=True)
    df =df.drop(['corridor_id'], axis = 1)
    df = df.groupby(['load_country']).sum().reset_index()
    df = df[df['intake']> 0] # filter values that are more than zero
    
    if not df_intake_previous.empty:
        intake_previous_df = df_intake_previous.drop(['commodity', 'date'], axis= 1)
        intake_previous_df.columns = ['corridor_id', 'intake',]
        df_last = pd.merge(df_corridor,intake_previous_df,on=['corridor_id'],how="outer",indicator=True)
        df_last =df_last.drop(['corridor_id'], axis = 1)
        df_last = df_last.groupby(['load_country']).sum().reset_index()

        new_df = pd.merge(df,df_last,on=['load_country'],how="left")
        
        new_df['percentage'] = new_df.apply(lambda row: percentual_var(row['intake_x'], row['intake_y']), axis = 1)
        new_df = new_df.sort_values(by=['intake_x'],ascending=False)
        new_df['intake_x'] = new_df['intake_x'].map(lambda x: "{:,}".format(int(x)), na_action='ignore')
        new_df['intake_y'] = new_df['intake_y'].map(lambda x: "{:,}".format(int(x)), na_action='ignore')
        new_df.columns = ['Country', 'Intake ' + str(year) + ' [Tons]', 'Intake ' + str(year-1) +  ' [Tons]','Var. [%]']
    else:
        new_df = df.copy(deep=True)
        new_df['intake_y'] = np.nan
        new_df['percentage'] = np.nan
        new_df.columns = ['Country', 'Intake ' + str(year) + ' [Tons]', 'Intake ' + str(year-1) +  ' [Tons]','Var. [%]']

    return new_df


def sidebar_oil_intake_content(country, year, year_intake):
    df_corridor = pd.DataFrame.from_records(Corridor.objects.filter(load_country = country).values('corridor_id', 'corridor_name'))
    df_intake =   pd.DataFrame.from_records(
            CorridorIntake.objects.filter(Q(date__year=year), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake'))
    df_intake.columns = ['corridor_id', 'intake']
    df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="inner",indicator=True)
    df = df.drop(['corridor_id'], axis = 1)
    year_intake = year_intake*1000000
    intake = 0
    df_dict = {}

    if not df.empty:
        df = df.groupby(['corridor_name']).sum().reset_index()
        intake = df['intake'].sum() 
        df['percentage_total'] = df['intake'].map(lambda x: round((x/year_intake)*100,2), na_action='ignore')
        df['percentage_country'] = df['intake'].map(lambda x: round((x/intake)*100,2), na_action='ignore')
        df = df.sort_values(by=['intake'],ascending=False)
        print(df.head(10))
        #df_dict = pd.Series(df.intake.values,index=df.corridor_name).to_dict()
        df_dict = df.set_index('corridor_name').T.to_dict('list')

    return df_dict, intake

def sidebar_discharge_port_oil(dp, year):
    query_df = pd.DataFrame.from_records(Corridor.objects.filter(discharge_port=dp).values('corridor_id', 'load_port'))
    intake_df = pd.DataFrame.from_records(
            CorridorIntake.objects.filter(Q(date__year=year), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake'))
    intake_df.columns = ['corridor_id', 'intake']
    df = pd.merge(query_df,intake_df,on=['corridor_id'],how="inner",indicator=True)

    dp_intake = 0
    df_dict = {}

    if not df.empty:
        df = df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['load_port']).sum().reset_index()
        df = df.sort_values(by=['intake'],ascending=False)
        dp_intake = df['intake'].sum()
        df_dict = df.set_index('load_port').T.to_dict('list')

    return df_dict, dp_intake    

