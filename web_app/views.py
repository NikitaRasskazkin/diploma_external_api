from django.shortcuts import render, reverse
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout

from common.api_utils import form_view


@login_required
@form_view
def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


@login_required
def logout(request: HttpRequest) -> HttpResponse:
    """"""
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
    """"""
    return render(request, 'user/profile.html')
