from django.shortcuts import render
from django.http import HttpResponse
from .models import Corridor , CorridorIntake
# Create your views here.


def home_view (request):
    context ={}
    return render(request,'stories/home.html', context)


def story_view (request):
    name = None
    if request.method == 'GET':
        name = request.GET.get('corridor_name')
    context = {
        'corridors' : Corridor.objects.all(),
        'select_corridor' : name
    }
    return render(request, 'stories/crude_story.html', context)

def story_ajax_view (request):
    if request.method == 'GET':
        id = request.GET.get('corridor_id')
        corridor = Corridor.objects.filter(corridor_id=id).first()
        
    context = {
        'corridors' : Corridor.objects.all().distinct('load_country'),
        'select_corridor' : corridor
        
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

def load_date(request):
    print('Aqui estoy2')
    print(request.GET)
    id = request.GET.get('id')
    SubCategory = CorridorIntake.objects.filter(corridor = id)#.order_by('name')
    #SubCategory = CorridorIntake.objects.all()#.order_by('name')
    print(SubCategory)
    context = {
        'date_list' : SubCategory,
        'select'        : "Date", 
    }
    return render(request, 'stories/ajax_load.html', context)
