from typing import cast

from django.shortcuts import render, reverse
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User

from common.api_utils import form_view
from report.service.report import ReportManager
from report.service.exceptions import ReportDoesNotExist
from report.models import Report


@login_required
@form_view
def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


@login_required
def logout(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        django_logout(request)
        return HttpResponseRedirect(reverse('web_app:login'))
    return HttpResponseNotAllowed(['GET'])


@form_view
def registration(request: HttpRequest) -> HttpResponse:
    return render(request, 'user/registration.html')


@login_required
@form_view
def profile(request: HttpRequest) -> HttpResponse:
    return render(request, 'user/profile.html', context={
        'reports': [
            {
                'id': report_data.pk,
                'text': report_data.text if len(report_data.text) < 100 else f'{report_data.text[:98]}...',
                'date': report_data.create_dttm,
            }
            for report_data in Report.objects.filter(user=request.user).order_by('-create_dttm')
        ]
    })


@login_required
@form_view
def report(request: HttpRequest, report_id: int) -> HttpResponse:
    try:
        report_info = ReportManager.load(report_id, cast(User, request.user)).get_report_info()
    except ReportDoesNotExist:
        raise Http404('Отчёт не найден')
    return render(request, 'report/report.html', context={'report': report_info})
