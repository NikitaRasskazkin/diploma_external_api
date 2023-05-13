from django.urls import path

from . import views


app_name = 'accounts'


urlpatterns = [
    path('', views.AccountCreate.as_view(), name='list'),
    path('<int:user_id>', views.AccountDetail.as_view(), name='detail'),
]
