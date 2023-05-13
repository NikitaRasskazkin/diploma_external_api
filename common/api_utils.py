from typing import Any, Callable, TypeVar, Type, ParamSpec, Concatenate
import json

from django.http import HttpRequest, HttpResponseNotAllowed, HttpResponse
from django.utils import timezone
from pydantic import BaseModel, ValidationError
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView


P = ParamSpec('P')
D = TypeVar('D', bound=BaseModel)

FormView = Callable[Concatenate[HttpRequest, P], HttpResponse]


def form_view(func: FormView) -> FormView:
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.method == 'GET':
            return func(request, *args, **kwargs)
        else:
            return HttpResponseNotAllowed(['GET'])
    return wrapper


def json_success_response(data: Any, status: int) -> Response:
    """Standard JSON response"""
    return Response({
        'success': True,
        'message': 'OK',
        'errors': [],
        'dttm': timezone.now(),
        'data': data,
    }, status=status)


def json_fail_response(message: str, errors: list, status: int, data: Any = None) -> Response:
    """JSON response with 4xx and 5xx statuses"""
    return Response(
        {
            'success': False,
            'message': message,
            'errors': errors,
            'dttm': timezone.now(),
            'data': data,
        },
        status=status
    )


def json_404(message: str, errors: list | None = None) -> Response:
    """JSON Bad Request response"""
    if errors is None:
        errors = ['DoesNotExist']
    return json_fail_response(message, errors, 404)


def json_bad_request(message: str, errors: list) -> Response:
    """JSON Bad Request response"""
    return json_fail_response(message, errors, 400)


def json_request(request_body: Type[D]):
    """
        Decorator to API method that contain JSON body.
        Extracts the JSON body from the request, validates the fields according to request_body,
        and converts to the request_body request data structure.
        The received data structure of the request passes the first arguments to the function.
        Arguments to the resulting function can only be passed as kvargs.
    """
    def decorator(
        func: Callable[Concatenate[APIView, Request, D, P], Response]
    ) -> Callable[Concatenate[APIView, Request, P], Response]:
        def wrapper(self: APIView, request: Request, *args, **kwargs) -> Response:
            try:
                data = request_body(**request.data)
            except ValidationError as e:
                return json_bad_request('JSON body validation error', e.errors())
            return func(self, request, data, *args, **kwargs)
        return wrapper
    return decorator
