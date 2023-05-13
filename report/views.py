from dataclasses import asdict

from django.http import HttpRequest, Http404
from django.shortcuts import get_object_or_404, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from pydantic import BaseModel, Field

from common.api_utils import json_request, json_bad_request, json_404, json_success_response
from .service.report import ReportManager
from .service import exceptions


class ReportCreateData(BaseModel):
    """Request body when creating a report."""
    text: str = Field(max_length=10000)


class ReportList(APIView):
    """
        Methods for interacting with reports set.
        POST: create report.
    """
    @json_request(ReportCreateData)
    def post(self, request: Request, data: ReportCreateData) -> Response:
        """Method to create account"""
        report_manager = ReportManager.create(data.text, request.user)
        report_manager.calculate()
        return json_success_response(asdict(report_manager.get_report_info()), 201)


class ReportDetail(APIView):
    """
        Methods of a specific report.
        GET: get report data.
    """
    @classmethod
    def get(cls, request: Request, report_id: int) -> Response:
        """Get public account information"""
        try:
            return json_success_response(
                asdict(ReportManager.load(report_id, request.user).get_report_info())
            )
        except exceptions.ReportDoesNotExist:
            return json_404(f'Report {report_id} does not exist')
