from os import execle
import pandas as pd
from stories.models import CorridorIntake, Corridor, CommodityLvh , CorridorFailure, Pipeline
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from datetime import datetime


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

def total_intake_variation_year(year):
    intake_df = pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year =year), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))
    intake_df_last = pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year = int(year)-1), Q(commodity=66)|Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))

    total_intake = (intake_df['intake'].sum())

    if intake_df_last.empty:
        variation = "No Data Available"
    else:
        total_intake_last = intake_df_last['intake'].sum()
        variation = round((((total_intake - total_intake_last) / total_intake_last) * 100),2)
    
    total_intake = round(total_intake/1000000,2)

    return total_intake, variation

def percentual_variation(year):
    df_corridor = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','load_country'))
    df_intake =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year=year), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))

    df_intake.columns = ['corridor_id', 'intake', 'date']
    df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
    df =df.drop(['corridor_id'], axis = 1)
    df = df.groupby(['load_country']).sum().reset_index()
    df = df[df['intake']> 0] # filter values that are more than zero
    total_sum = df['intake'].sum()
    df['percentage'] = df['intake'].apply(lambda x: round((x/total_sum)*100,2))
    top_five_df = df.nlargest(5,'intake')
    top_five_df['intake'] =  df['intake'].apply(lambda x: round((x/1000000),2))


    top_five = top_five_df.drop(['intake'], axis = 1)
    top_five_dic = pd.Series(top_five.percentage.values,index=top_five.load_country).to_dict()
    
    top_five_df.columns = ['Port','Intake [MTons]', 'Percentage [%]']
  
    return top_five_dic, df , top_five_df

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
    
    df2 = pd.merge(ports, intake_df_last, on=['corridor'],how="outer")

    if intake_df_last.empty:
        variation = "No Data Available"
    else:
        total_intake_last = df2['intake'].sum()
        variation = round((((intake - total_intake_last) / total_intake_last) * 100),2)
    
    df = pd.merge(ports, df_intake, on=['corridor'],how="outer")
    df =df.drop(['corridor','discharge_port'], axis = 1)
    df = df.groupby(['load_port']).sum().reset_index()
    df = df[df['intake']> 0] 
    top_three = df.nlargest(3,'intake')
    top_three_dict = pd.Series(top_three.intake.values,index=top_three.load_port).to_dict()

    print(percentage)
    print(intake)
    

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
   
    df2_l =df2.drop(['corridor','discharge_port'], axis = 1)
    df2_l = df2_l.groupby(['load_port']).sum().reset_index()
    load_port_intake_last = df2_l['intake'][df2_l['load_port']== corridor[0].get('load_port')].values[0]

    if intake_df_last.empty:
        load_port_variation = "No Data Available"
    else:
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
    
    df3 =df2.drop(['corridor','load_port'], axis = 1)
    df3 = df3.groupby(['discharge_port']).sum().reset_index()
    discharge_port_intake_last = df3['intake'][df3['discharge_port']== corridor[0].get('discharge_port')].values[0]

    if intake_df_last.empty:
        discharge_port_variation = "No Data Available"
    else:
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