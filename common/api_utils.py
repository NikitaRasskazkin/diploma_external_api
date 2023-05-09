from typing import Any, Callable, TypeVar, Type, ParamSpec, Concatenate
import json

from django.http import HttpRequest
from django.utils import timezone
from pydantic import BaseModel, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView


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


P = ParamSpec('P')
D = TypeVar('D', bound=BaseModel)


def json_request(request_body: Type[D]):
    """
        Decorator to API method that contain JSON body.
        Extracts the JSON body from the request, validates the fields according to request_body,
        and converts to the request_body request data structure.
        The received data structure of the request passes the first arguments to the function.
        Arguments to the resulting function can only be passed as kvargs.
    """
    def decorator(
        func: Callable[Concatenate[APIView, HttpRequest, D, P], Response]
    ) -> Callable[Concatenate[APIView, HttpRequest, P], Response]:
        def wrapper(self: APIView, request: HttpRequest, *args, **kwargs) -> Response:
            try:
                data = request_body(**json.loads(request.body.decode('utf-8')))
            except ValidationError as e:
                return json_bad_request('JSON body validation error', e.errors())
            return func(self, request, data, *args, **kwargs)
        return wrapper
    return decorator
