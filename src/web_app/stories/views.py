from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from plotly.offline import plot
import plotly.graph_objs as go
from .models import Corridor , CorridorIntake, CorridorPipeline, Pipeline, CommodityLvh

from django.db.models import Sum
# Create your views here.

def home_view (request):
    context ={}
    return render(request,'stories/home.html', context)


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
    if request.method == 'GET':
        id = request.GET.get('corridor_id')
        corridor = Corridor.objects.filter(corridor_id=id).first()
        pipeline = request.GET.get('pipe_id')

    data = list(CorridorIntake.objects.values_list('commodity').annotate(Sum('intake'))) #Return a tumple of (commodity, sum)

    x_data,y_data = [list(c) for c in zip(*data)] #Separete x and y data by commodity and sum(intake)
    #x_data = [str(int) for int in x_data]

    x_data = [CommodityLvh.objects.values_list('name').filter(commodity_id=int)[0][0] for int in x_data] #Query returns a tuple Queryset[(name, )] 

    barplot = go.Figure([go.Bar(x=x_data, y=y_data,
                        name='test',
                        opacity=0.8, marker_color='green')])

    barplot.update_layout(
                        title='Total Intake per Commodity',
                        width = 500,
                        height = 500,
                    )
    plot_div = plot(barplot, output_type='div')
    '''
    
    plot_div = plot([go.Bar(x=x_data, y=y_data,
                        name='test',
                        opacity=0.8, marker_color='green')],
               output_type='div')
    '''
    context = {
        'corridors' : Corridor.objects.all().distinct('load_country'),
        'select_corridor' : corridor,
        'plot_div': plot_div
        
    }

    #print(co)
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
