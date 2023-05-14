from django.core.exceptions import ObjectDoesNotExist


class ReportDoesNotExist(ObjectDoesNotExist):
    """The report does not exist"""


class ReportNotInCalculationQueue(Exception):
    """The report is not in the calculation queue"""
