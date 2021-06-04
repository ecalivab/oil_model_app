from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from .forms import UserPasswordResetForm, UserSetPasswordForm
urlpatterns = [
    path('', home_view, name='stories_home'),

    path('second/', story_view, name='story'),
    path('ajax/', story_ajax_view, name='story_ajax'),
    path('oil/', story_oil_view, name='story_oil'),
    path('oil_intake/', oil_intake_story_view, name='story_oil_intake'),
    path('oil_discharge_port/', discharge_port_oil_story_view, name='story_dicharge_port_oil'),
    path('commodity_discharge_port/', discharge_port_commodity_view, name='story_dicharge_port_commodity'),
    path('risk_suppliers/', risk_crude_suppliers_view, name='story_risk_suppliers'),
    
    path('ajax/load_corrdior/', load_corridor, name='ajax_load_corridor'),
    path('ajax/load_pipe/', load_pipe, name='ajax_load_pipe'),
    path('ajax/load_port/', load_port, name='ajax_load_port'),
    path('ajax/discharge_port/', discharge_port, name='ajax_discharge_port'),
    path('ajax/side_bar_intake/', sidebar_oil_intake, name='ajax_sidebar_oil_intake'),
    path('ajax/side_bar_dicharge_port_oil/', sidebar_oil_discharge_intake, name='ajax_sidebar_dicharge_port_oil'),
    path('ajax/side_bar_dicharge_port_commodity/', sidebar_commodity_discharge_intake, name='ajax_sidebar_dicharge_port_commodity'),
    path('ajax/side_bar_risk_oil/', sidebar_risk_oil ,name='ajax_sidebar_risk_oil'),
    path('ajax/tables_risk/',tables_risk_change_units, name= 'ajax_tables_risk'),

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