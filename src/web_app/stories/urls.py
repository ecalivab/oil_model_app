from django.urls import path
from .views import story_view, home_view ,story_ajax_view ,load_corridor , load_pipe, login_view, sign_up_view, princing_view, logout_view , contact_view, activate_view
from django.contrib.auth import views as auth_views
from .forms import UserPasswordResetForm, UserSetPasswordForm
urlpatterns = [
    path('', home_view, name='stories_home'),
    path('second/', story_view, name='story'),
    path('ajax/', story_ajax_view, name='story_ajax'),
    path('ajax/load_corrdior/', load_corridor, name='ajax_load_corridor'),
    path('ajax/load_pipe/', load_pipe, name='ajax_load_pipe'),
    path('pricing/', princing_view, name='pricing'),
    path('contact/', contact_view, name='contact'),

    path('users/login/', login_view, name='login'),
    path('users/sign_up/', sign_up_view, name='sign_up'),
    path('logout/', logout_view, name='logout'),
    path('users/activate/<uidb64>/<token>/', activate_view, name='activate'),

    path("users/password_reset/", auth_views.PasswordResetView.as_view(template_name="stories/users/password_reset.html", form_class=UserPasswordResetForm), name="password_reset"),
    path("users/password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="stories/users/password_reset_done.html"), name="password_reset_done"),
    path("users/password_reset_confirm/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(template_name="stories/users/password_reset_confirm.html",form_class=UserSetPasswordForm), name="password_reset_confirm"),
    path("users/password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="stories/users/password_reset_complete.html"), name="password_reset_complete"),    
]