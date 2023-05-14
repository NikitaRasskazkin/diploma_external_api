from typing import Self
from enum import Enum
from dataclasses import dataclass

from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from ..models import Report
from .exceptions import ReportDoesNotExist, ReportNotInCalculationQueue
from .calculation_manager import calculation_manager


class ReportStatus(str, Enum):
    WAITING = 'WAITING'
    IN_PROCESS = 'IN_PROCESS'
    COMPLETED = 'COMPLETED'
    ERROR = 'ERROR'


@dataclass()
class ReportUrls:
    page: str
    api: str


@dataclass()
class ReportInfo:
    id: int
    text: str
    status: ReportStatus
    user: int
    queue_place: int | None
    urls: ReportUrls


class ReportManager:
    def __init__(self, report: Report) -> None:
        self.report = report

    @classmethod
    def load(cls, report_id: int, user: User | None = None) -> Self:
        try:
            report_manager = ReportManager(Report.objects.get(pk=report_id))
            if user is not None and report_manager.report.user.pk != user.pk:
                raise ObjectDoesNotExist()
            return report_manager
        except ObjectDoesNotExist:
            raise ReportDoesNotExist(f'The report {report_id} does not exist')

    @classmethod
    def create(cls, text: str, user: User) -> Self:
        report = Report(text=text, user=user, status=Report.ReportStatus.WAITING, create_dttm=timezone.now())
        report.save()
        return ReportManager(report)

    def calculate(self) -> None:
        calculation_manager.calculate(self.report)

    def get_report_info(self) -> ReportInfo:
        if self.report.status == Report.ReportStatus.WAITING:
            try:
                queue_place = calculation_manager.get_queue_place(self.report.pk)
            except ReportNotInCalculationQueue:
                queue_place = None
                self.report.refresh_from_db()
        else:
            queue_place = None
        statuses = {
            'W': 'WAITING',
            'P': 'IN_PROCESS',
            'C': 'COMPLETED',
            'E': 'ERROR',
        }
        return ReportInfo(
            id=self.report.pk,
            text=self.report.text,
            status=ReportStatus[statuses[self.report.status]],
            user=self.report.user.pk,
            queue_place=queue_place,
            urls=ReportUrls(
                reverse('web_app:report', kwargs={'report_id': self.report.pk}),
                reverse('report:detail', kwargs={'report_id': self.report.pk}),
            ),
        )
