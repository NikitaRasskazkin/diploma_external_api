from typing import Callable
from threading import Thread

import requests
from pydantic import BaseModel
from django.utils import timezone

from common.settings import MODELS_HOSTS, WORKERS_BY_MODEL
from ..models import Report, ReportLog, ReportRecognition
from .exceptions import ReportNotInCalculationQueue


class Recognition(BaseModel):
    """Prediction body for one sentence"""
    sentence: str
    is_paraphrase: bool
    probability: float


class ModelResponse(BaseModel):
    """Response from the model service"""
    version: str
    source_text: str
    recognition: list[Recognition]
    recognition_time: str


class Worker:
    """
        Class for generating a report.
        Contains the URL of the host of the service model on which the report will be calculated.
    """
    def __init__(self, worker_id: int, url: str, finish_callback: Callable[[int], None]):
        self.__worker_id = worker_id
        self.__url = url
        self.__finish_callback = finish_callback

    @property
    def id(self) -> int:
        return self.__worker_id

    def start(self, report: Report) -> None:
        """Generates a report and saves the results in DB."""
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
    """
        Report calculation manager. Allows you to calculate several reports in parallel
        on several services of the model, and also forms a queue waiting for reports to be generated.
    """
    def __init__(self, models_hosts: list, workers_by_model: int) -> None:
        self.__workers = self.__build_workers(models_hosts, workers_by_model)
        self.__queue: list[Report] = []
        self.__free_workers = list(self.__workers.values())

    def calculate(self, report: Report) -> None:
        """Add a report to the queue for generation."""
        try:
            worker = self.__free_workers.pop(0)
        except IndexError:
            self.__queue.append(report)
            return
        Thread(target=worker.start, args=(report,)).start()

    def get_queue_place(self, report_id: int) -> int:
        """Get a report place in the queue"""
        queue: list[int] = [report.pk for report in self.__queue.copy()]
        try:
            return queue.index(report_id) + 1
        except ValueError:
            raise ReportNotInCalculationQueue(f'Report {report_id} is not in calculation queue')

    def _release_work(self, worker_id: int) -> None:
        self.__free_workers.append(self.__workers[worker_id])
        try:
            text = self.__queue.pop(0)
        except IndexError:
            return
        self.calculate(text)

    def __build_workers(self, models_hosts: list, workers_by_model: int) -> dict[int, Worker]:
        workers: dict[int, Worker] = {}
        worker_id = 0
        for host in models_hosts:
            for _ in range(workers_by_model):
                workers.update({worker_id: Worker(worker_id, host, self._release_work)})
                worker_id += 1
        return workers


calculation_manager = ReportCalculationManager(MODELS_HOSTS, WORKERS_BY_MODEL)
