from django.http import HttpRequest, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from pydantic import BaseModel, Field

from common.api_utils import json_request, json_bad_request, json_404, json_success_response


class AccountCreateData(BaseModel):
    """Request body when creating an account"""
    user_name: str = Field(max_length=20)
    password: str = Field(max_length=20)


class AccountCreate(APIView):
    """Create user account"""
    permission_classes = [AllowAny]

    @json_request(AccountCreateData)
    def post(self, request: Request, data: AccountCreateData) -> Response:
        """Method to create account"""
        try:
            User.objects.create_user(data.user_name, password=data.password)
        except IntegrityError:
            return json_bad_request('Such a username already exists', errors=['UserNameError'])
        user = authenticate(username=data.user_name, password=data.password)
        login(request, user)
        response = {'user': {'id': user.pk, **data.dict()}}
        return json_success_response(response, 201)


class AccountDetail(APIView):
    """Methods of a specific account"""
    def get(self, request: Request, user_id: int) -> Response:
        """Get public account information"""
        try:
            account = get_object_or_404(User, pk=user_id)
        except Http404:
            return json_404(f'Account with id {user_id} does not exist')
        return Response({'user_name': account.username})
