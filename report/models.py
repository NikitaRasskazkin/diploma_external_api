from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy


class Report(models.Model):
    class ReportStatus(models.TextChoices):
        WAITING = "W", gettext_lazy('WAITING')
        IN_PROCESS = "P", gettext_lazy('IN_PROCESS')
        COMPLETED = "C", gettext_lazy('COMPLETED')
        ERROR = "E", gettext_lazy('ERROR')

    id = models.AutoField
    text = models.TextField()
    status = models.CharField(max_length=3, choices=ReportStatus.choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
