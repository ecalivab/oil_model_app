from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from plotly.offline import plot
from .forms import ContactForm, SignUpForm, LogInForm
from .models import Corridor , CorridorIntake, CorridorPipeline, Pipeline, CommodityLvh
from utils.utils_plot import *
from datetime import datetime

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, BadHeaderError, EmailMessage

from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

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
        form = LogInForm(request.POST)
        if form.is_valid():
            username =  form.cleaned_data['username']
            password = form.cleaned_data['passwd']
            user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('stories_home')
        else:
            messages.error(request, 'Username OR password is incorrect')
            
    form = LogInForm()
    context ={'form': form}
    return render(request,'stories/login.html', context )

def logout_view(request):
	logout(request)
	return redirect('login')


def sign_up_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username = form.cleaned_data.get('email'),
                    password = form.cleaned_data.get('password1'),
                    first_name = form.cleaned_data.get('first_name'),
                    last_name = form.cleaned_data.get('last_name')
                )
                user.profile.type = 'F'
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('stories/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                 })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()

               
                messages.success(request, 'Account was created for ' + user.first_name + ' Please confirm your email address to complete the registration')
                return redirect('login')

            except:
                 messages.error(request, "User already Exist!")
                 return render(request = request, template_name = 'stories/sign_up.html', context={'form':form})
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
            
            return render(request = request, template_name = 'stories/sign_up.html', context={'form':form})

    form = SignUpForm()
    context={ 'form': form}
    return render(request,'stories/sign_up.html', context)

def activate_view (request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!' )
        return redirect('login')


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
    current_date = datetime.today().strftime('%m/%d/%Y')
    end_date = datetime.today().strftime('%Y-%m-%d')
    year = current_date.split("/")[2]
    first_date = "01/01/%s" % year
    start_date = "%s-01-01" % year

    if request.method == 'POST':
        id = request.POST.get('corridor_id')
        corridor = Corridor.objects.filter(corridor_id=id).first()
        pipeline = request.POST.get('pipe_id')
        daterange = request.POST.get('daterange')

        #Fix date formats to make them compatible 
        daterange = daterange.split("-")
        end_date = daterange[1].strip()
        current_date = end_date
        end_date = datetime.strptime(end_date, '%m/%d/%Y')
        start_date = daterange[0].strip()
        first_date= start_date
        start_date = datetime.strptime(start_date, '%m/%d/%Y')
        end_date = end_date.strftime('%Y-%m-%d')
        start_date = start_date.strftime('%Y-%m-%d')

        #BarPlot
        corridor_intake = pd.DataFrame.from_records(
            CorridorIntake.objects.filter(corridor=id, date__lte=end_date, date__gte=start_date).values('commodity','intake'))
        lhv = pd.DataFrame.from_records(
            CommodityLvh.objects.all().values('commodity_id', 'name'))
        
        bar = intake_corridor_barplot(corridor_intake, lhv)
        bar_div = plot(bar, output_type='div' )

   
    #World Map Color Plot
    corridor_df = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','load_country'))
    intake_df =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__lte=end_date), Q(date__gte=start_date), Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date')) #missing filter per date?

    fig = world_choropleth_map(corridor_df, intake_df)
    world_plot_div = plot(fig, output_type='div')

    context = {
        'corridors' : Corridor.objects.all().distinct('load_country'),
        'select_corridor' : corridor,
        'plot_div': world_plot_div, 
        'bar_div': bar_div,
        'curr_date': current_date,
        'start_date': first_date,     
    }

    return render(request, 'stories/crude_ajax.html', context)


def load_corridor(request):
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
