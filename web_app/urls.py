from django.urls import path
from django.contrib.auth.views import LoginView
from . import views


app_name = 'web_app'


LoginView.template_name = 'user/login.html'

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', LoginView.as_view(), name="login"),
    path('accounts/logout/', views.logout, name="logout"),
    path('accounts/registration/', views.registration, name="registration"),
    path('accounts/profile/', views.profile, name="profile"),
]
