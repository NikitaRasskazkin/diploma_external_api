from typing import Self, Callable

import requests
from pydantic import BaseModel
from django.utils import timezone

from ..models import Report, ReportLog, ReportRecognition


class Recognition(BaseModel):
    sentence: str
    is_paraphrase: bool
    probability: float


class ModelResponse(BaseModel):
    version: str
    source_text: str
    recognition: list[Recognition]
    recognition_time: str


class Worker:
    def __init__(self, worker_id: int, url: str, finish_callback: Callable[[int], None]):
        self.__worker_id = worker_id
        self.__url = url
        self.__finish_callback = finish_callback

    @property
    def id(self) -> int:
        return self.__worker_id

    def start(self, report: Report) -> None:
        report.calculation_start_dttm = timezone.now()
        report.status = Report.ReportStatus.IN_PROCESS
        report.save()
        try:
            response = ModelResponse(**requests.post(self.__url, json={'text': report.text}).json()['data'])
            ReportRecognition.objects.bulk_create([
                ReportRecognition(
                    report=report,
                    sentence=recognition.sentence,
                    is_paraphrase=recognition.is_paraphrase,
                    probability=recognition.probability,
                )
                for recognition in response.recognition
            ])
            report.model_version = response.version
            report.status = Report.ReportStatus.COMPLETED
        except Exception as e:
            report.status = Report.ReportStatus.ERROR
            ReportLog.objects.create(report=report, error=str(e))
            raise e
        finally:
            report.calculation_end_dttm = timezone.now()
            report.save()
            self.__finish_callback(self.id)


class ReportCalculationManager:
    def __init__(self) -> None:
        pass

    def calculate(self, report: Report) -> None:
        pass


worker = Worker(1, 'http://127.0.0.1:5000/api/v1.0/recognition', lambda x: x)
