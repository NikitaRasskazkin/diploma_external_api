from django.core.exceptions import ObjectDoesNotExist


class ReportDoesNotExist(ObjectDoesNotExist):
    """The report does not exist"""
