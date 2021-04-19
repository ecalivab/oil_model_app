from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from plotly.offline import plot
import plotly.graph_objs as go
from .models import Corridor , CorridorIntake, CorridorPipeline, Pipeline, CommodityLvh
from utils.utils_plot import *

from django.db.models import Sum
# Create your views here.

def home_view (request):
    context ={}
    return render(request,'stories/home.html', context)

def login_view(request):
    context={}
    return render(request,'stories/login.html', context )

def sign_up_view(request):
    context ={}
    return render(request,'stories/sign_up.html', context)

def princing_view(request):
    context ={}
    return render(request, 'stories/pricing.html',context)

def story_view (request):
    
    name = None
    if request.method == 'POST':
        print('ENTRE')
        name = request.POST.get('corridor')
        if Corridor.objects.filter(corridor_name=name).exists():
            pass
        else:
            name = "INVALID CORRIDOR"
    context = {
        'select_corridor' : name
    }
    

    if request.is_ajax():
        q = request.GET.get('term','')
        corridors = Corridor.objects.filter(corridor_name__istartswith=q)
        result = []
        for n in corridors:
            name_json = n.corridor_name
            result.append(name_json)
        return JsonResponse(result, safe=False)

    return render(request, 'stories/crude_story.html', context)

def story_ajax_view (request):
    corridor = None
    bar_div = None
    if request.method == 'POST':
        id = request.POST.get('corridor_id')
        corridor = Corridor.objects.filter(corridor_id=id).first()
        pipeline = request.POST.get('pipe_id')
        daterange = request.POST.get('daterange')
        #BarPlot
        corridor_intake = pd.DataFrame.from_records(
            CorridorIntake.objects.filter(corridor=id).values('commodity','intake'))
        lhv = pd.DataFrame.from_records(
            CommodityLvh.objects.all().values('commodity_id', 'name'))
        
        bar = intake_corridor_barplot(corridor_intake, lhv)
        bar_div = plot(bar, output_type='div' )

    #World Map Color Plot
    corridor_df = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','load_country'))
    intake_df =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake')) #missing filter per date?

    fig = world_choropleth_map(corridor_df, intake_df)
    world_plot_div = plot(fig, output_type='div')

    context = {
        'corridors' : Corridor.objects.all().distinct('load_country'),
        'select_corridor' : corridor,
        'plot_div': world_plot_div, 
        'bar_div': bar_div,     
    }

    return render(request, 'stories/crude_ajax.html', context)


def load_corridor(request):
    print('Aqui estoy')
    print(request.GET)
    l_country = request.GET.get('country')
    SubCategory = Corridor.objects.filter(load_country__startswith=l_country)#.order_by('name')
    context = {
        'corridor_list' : SubCategory,
        'select'        : "Corridor", 
    }
    return render(request, 'stories/ajax_load.html', context)

def load_pipe(request):
    pipelines_names = [] 
    print(request.GET)
    id = request.GET.get('id')
    SubQuery = CorridorPipeline.objects.filter(corridor = id).values('pipeline')#.order_by('name')

    for i in range(0, len(SubQuery)):
        dic = {}
        pipeline_q = SubQuery[i]['pipeline']
        name = Pipeline.objects.filter(pipeline_id = pipeline_q).values('name')
        print(pipeline_q)
        dic['name'] = name[0]['name']
        dic['id'] = pipeline_q
        pipelines_names.append(dic) 
    
    context = {
        'pipe_list' : pipelines_names,
        'select'        : "Pipe", 
    }
    return render(request, 'stories/ajax_load.html', context)
