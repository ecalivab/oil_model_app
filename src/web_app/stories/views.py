from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from plotly.offline import plot
from .forms import ContactForm
from .models import Corridor , CorridorIntake, CorridorPipeline, Pipeline, CommodityLvh , Profile
from utils.utils_plot import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, BadHeaderError

# Create your views here.

def home_view (request):
    context ={}
    return render(request,'stories/home.html', context)

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Website Inquiry" 
            body = {
                'first_name': form.cleaned_data['first_name'], 
			    'last_name': form.cleaned_data['last_name'], 
			    'email': form.cleaned_data['email_address'], 
			    'message':form.cleaned_data['message'], 
			    }
            message = "\n".join(body.values())
            
            try:
                send_mail(subject, message, 'admin@example.com', ['admin@example.com']) 
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            
            return redirect ("stories_home")

    form = ContactForm()
    context ={
        'form': form,
    }
    return render(request, 'stories/contact.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password =request.POST.get('passwd')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('stories_home')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context={}
    return render(request,'stories/login.html', context )

def logout_view(request):
	logout(request)
	return redirect('login')


def sign_up_view(request):
    if request.method == 'POST':
        if (request.POST.get('flag') == 'signIn' or request.POST.get('name') is not None or request.POST.get('surname') is not None or request.POST.get('email') is not None or request.POST.get('passwd') is not None):
            user = User.objects.create_user(
                username=request.POST.get('email'), password=request.POST.get('passwd'), first_name=request.POST.get('name'),
                last_name=request.POST.get('last_name')
                )
            user.profile.type = 'F'
            user.save()

            messages.success(request, 'Account was created for ' + user.first_name)
            
            return redirect('login')

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
