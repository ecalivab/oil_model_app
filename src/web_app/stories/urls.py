from django.urls import path
from .views import story_view, home_view ,story_ajax_view , load_corridor , load_date

urlpatterns = [
    path('', home_view, name='stories_home'),
    path('second', story_view, name='story'),
    path('ajax/', story_ajax_view, name='story_ajax'),
    path('ajax/load_corrdior/', load_corridor, name='ajax_load_corridor'),
    path('ajax/load_date/', load_date, name='ajax_load_date'),
]