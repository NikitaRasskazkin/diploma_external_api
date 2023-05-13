from django.urls import path

from . import views


app_name = 'report'


urlpatterns = [
    path('', views.ReportList.as_view(), name='list'),
    path('<int:report_id>', views.ReportDetail.as_view(), name='detail'),
]
