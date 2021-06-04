import pandas as pd
from stories.models import CorridorIntake, Corridor, CommodityLvh ,Pipeline, CorridorFailure, CorridorPipeline
from django.db.models import Q, Subquery

def risk_single_corridor_crude (corridor_id, country, year): #The Pipeline ID should be pass as argument so the user can choose which route wants
    single_risk_df = pd.DataFrame(columns=['corridor_id','country','pipeline_id','risk'])

    intake_df = pd.DataFrame.from_records(CorridorIntake.objects.filter(Q(date__year=year), Q(corridor = corridor_id), Q(commodity=66)|Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','commodity','intake'))
    failure = pd.DataFrame.from_records(CorridorFailure.objects.filter(corridor = corridor_id, year=2019).values('pipeline','corridor_failure_captive'))
    
    if failure.empty == False:
        failure.columns = ['pipeline_id', 'corridor_failure_captive']
   
        if intake_df.empty == False:
            intake_df = intake_df.groupby(['corridor','commodity']).agg({'intake': 'sum',}).reset_index()
        
        corridor_pipeline = CorridorPipeline.objects.filter(corridor= corridor_id)
        pipeline_df = pd.DataFrame.from_records(Pipeline.objects.filter(pipeline_id__in = Subquery(corridor_pipeline.values('pipeline'))).values('pipeline_id','share_val'))    
        if pipeline_df.empty == False:
            new_df = pd.merge(pipeline_df,failure,on=['pipeline_id'],how="outer")
            for _, row_i in intake_df.iterrows():
                lvh = CommodityLvh.objects.values_list('lvh', flat=True).get(commodity_id = row_i['commodity'])
                for _, row_j in new_df.iterrows():
                    risk = row_i['intake']*row_j['share_val']*row_j['corridor_failure_captive']*lvh*0.2778*0.0860
                    row_dict = {'corridor_id':corridor_id,'country':country,'pipeline_id':row_j['pipeline_id'],'risk':risk}
                    single_risk_df=single_risk_df.append(row_dict, ignore_index=True)
        
    return single_risk_df

def risk_corridor_crude(year):
    corridors_df = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','load_country').order_by('load_country'))
    total_risk_df = pd.DataFrame(columns=['corridor_id','country','pipeline_id','risk'])
    for _, row in corridors_df.iterrows():
        single_risk_df = risk_single_corridor_crude (row['corridor_id'], row['load_country'], year)
        total_risk_df = total_risk_df.append(single_risk_df, ignore_index=True)
    total_risk_df = total_risk_df.drop(['pipeline_id'], axis=1) 
    total_risk_df = total_risk_df.groupby(['country']).sum().reset_index()
    
    max = total_risk_df[total_risk_df['risk']==total_risk_df['risk'].max()]
    min = total_risk_df[total_risk_df['risk']==total_risk_df['risk'].min()]
    risk_dict = {'max_c': max['country'].values[0], 'max_r': round(max['risk'].values[0]/1000000,4), 'min_c':min['country'].values[0], 'min_r': round(min['risk'].values[0]/1000000,4)}

    return risk_dict, total_risk_df

def risk_single_corridor_crude_daterange(corridor_id, country, start_date, end_date):
    single_risk_df = pd.DataFrame(columns=['corridor_id','country','pipeline_id','risk', 'intake'])

    intake_df = pd.DataFrame.from_records(CorridorIntake.objects.filter(Q(date__lte=end_date), Q(date__gte=start_date), Q(corridor = corridor_id), Q(commodity=66)|Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','commodity','intake'))
    failure = pd.DataFrame.from_records(CorridorFailure.objects.filter(corridor = corridor_id, year=2019).values('pipeline','corridor_failure_captive'))
    
    if failure.empty == False:
        failure.columns = ['pipeline_id', 'corridor_failure_captive']
   
        if intake_df.empty == False:
            intake_df = intake_df.groupby(['corridor','commodity']).agg({'intake': 'sum',}).reset_index()
        
        corridor_pipeline = CorridorPipeline.objects.filter(corridor= corridor_id)
        pipeline_df = pd.DataFrame.from_records(Pipeline.objects.filter(pipeline_id__in = Subquery(corridor_pipeline.values('pipeline'))).values('pipeline_id','share_val')) 
        if pipeline_df.empty == False:
            new_df = pd.merge(pipeline_df,failure,on=['pipeline_id'],how="outer")
            for _, row_i in intake_df.iterrows():
                lvh = CommodityLvh.objects.values_list('lvh', flat=True).get(commodity_id = row_i['commodity'])
                for _, row_j in new_df.iterrows():
                    risk = row_i['intake']*row_j['share_val']*row_j['corridor_failure_captive']*lvh*0.2778*0.0860
                    row_dict = {'corridor_id':corridor_id,'country':country,'pipeline_id':row_j['pipeline_id'],'risk':risk, 'intake':(row_i['intake']*row_j['share_val'])}
                    single_risk_df=single_risk_df.append(row_dict, ignore_index=True)
        
    return single_risk_df

def risk_corridor_datarange_crude(start_date, end_date):
    corridors_df = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','load_country','corridor_name').order_by('load_country'))
    total_risk_df = pd.DataFrame(columns=['corridor_id','country','pipeline_id','risk', 'intake'])
    for _, row in corridors_df.iterrows():
        single_risk_df = risk_single_corridor_crude_daterange (row['corridor_id'], row['load_country'], start_date, end_date)
        total_risk_df = total_risk_df.append(single_risk_df, ignore_index=True)
    total_risk_df = total_risk_df.drop(['pipeline_id'], axis=1) 


    single_country_df = pd.merge(total_risk_df, corridors_df, on=['corridor_id'], how='left')
    single_country_df = single_country_df.drop(['load_country','corridor_id'], axis=1)
    total_risk_df = total_risk_df.drop(['corridor_id'], axis=1) 

    total_risk_df = total_risk_df.groupby(['country']).sum(['risk', 'intake']).reset_index()
    total_risk = total_risk_df['risk'].sum()
    
    
    total_risk_df = total_risk_df[total_risk_df['risk'] > 0]

    total_risk_df['percentage'] = total_risk_df['risk'].apply(lambda x: round((x/total_risk)*100,2))
    total_risk_df = total_risk_df.sort_values(by=['risk'],ascending=False)

    total_risk_df.columns = ['Country', 'Energy Risk [Mtoe]', 'Intake [Mtoe]', 'Share Risk [%]']

    top_three = total_risk_df.head(3).copy()
    tail_three = total_risk_df.tail(3).copy()

    return total_risk_df, top_three, tail_three, total_risk, single_country_df

    