from django.urls import path
from .views import story_view, home_view ,story_ajax_view , load_corridor , load_pipe, login_view, sign_up_view, princing_view, logout_view

urlpatterns = [
    path('', home_view, name='stories_home'),
    path('second/', story_view, name='story'),
    path('ajax/', story_ajax_view, name='story_ajax'),
    path('ajax/load_corrdior/', load_corridor, name='ajax_load_corridor'),
    path('ajax/load_pipe/', load_pipe, name='ajax_load_pipe'),
    path('login/', login_view, name='login'),
    path('sign_up/', sign_up_view, name='sign_up'),
    path('logout/', logout_view, name='logout'),
    path('pricing/', princing_view, name='pricing'),
]