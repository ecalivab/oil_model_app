import pandas as pd
from stories.models import CorridorIntake, Corridor
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
        CorridorIntake.objects.filter(Q(date__lte=end_date), Q(date__gte=start_date), Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))
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
     CorridorIntake.objects.filter(Q(date__lte=end_date), Q(date__gte=start_date), Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))
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
        CorridorIntake.objects.filter(Q(date__year =year), Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))
    intake_df_last = pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year = int(year)-1), Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))

    total_intake = intake_df['intake'].sum()

    if intake_df_last.empty:
        variation = "No Data Available"
    else:
        total_intake_last = intake_df_last['intake'].sum()
        variation = (((total_intake - total_intake_last) / total_intake_last) * 100).round(4)
      
    return total_intake, variation

def percentual_variation(year):
    df_corridor = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','load_country'))
    df_intake =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year=year), Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))

    df_intake.columns = ['corridor_id', 'intake', 'date']
    df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
    df =df.drop(['corridor_id'], axis = 1)
    df = df.groupby(['load_country']).sum().reset_index()
    df = df[df['intake']> 0] # filter values that are more than zero
    total_sum = df['intake'].sum()
    top_five = df.nlargest(5,'intake')
    top_five_list = list(top_five['load_country'])
    top_five['percentage'] = top_five['intake'].apply(lambda x: (x/total_sum).round(4)*100)

    top_five = top_five.drop(['intake'], axis = 1)
    top_five_dic = pd.Series(top_five.percentage.values,index=top_five.load_country).to_dict()

    return top_five_list, top_five_dic