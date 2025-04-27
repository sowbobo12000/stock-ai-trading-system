from django.db import models

class CrawlStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'

class AnalysisStatus(models.TextChoices):
    NOT_ANALYZED = 'NOT_ANALYZED', 'Not analyzed'
    ANALYZING = 'ANALYZING', 'Analyzing'
    ANALYZED = 'ANALYZED', 'Analyzed'