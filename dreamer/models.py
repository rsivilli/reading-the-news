from django.db import models
from newsfeed.models import Article
from datetime import datetime
import json


# Create your models here.
class ArticleImage(models.Model):
    image_location = models.CharField(max_length=255, null=False, blank=False)
    paragraph_number = models.SmallIntegerField(blank=False, null=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class ArticleAudio(models.Model):
    location = models.CharField(max_length=255, null=False, blank=False)
    paragraph_number = models.SmallIntegerField(blank=False, null=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class ArticleVideo(models.Model):
    location = models.CharField(max_length=255, null=False, blank=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class JobStatus(models.TextChoices):
    QUEUED = "Q"
    IN_PROGRESS = "I"
    COMPLETE_SUCCESS = "C"
    COMPLETE_ERROR = "E"
    COMPLETE_OVERRIDDEN = "O"


class JobType(models.TextChoices):
    IMAGE_GEN_FULL = "IGF"
    IMAGE_GEN_PARTIAL = "IGP"
    AUDIO_GEN_FULL = "AGF"
    AUDIO_GEN_PARTIAL = "AGP"
    VIDEO_GEN = "VG"


class DreamJob(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    job_status = models.CharField(
        max_length=1, choices=JobStatus.choices, default=JobStatus.QUEUED
    )
    job_type = models.CharField(
        max_length=3, choices=JobType.choices, null=False, blank=False
    )
    status_message = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(
        null=False, blank=False, default=datetime.now
    )
    updated_time = models.DateTimeField(
        null=False, blank=False, default=datetime.now
    )

    job_args = models.TextField(blank=True)

    @property
    def job_args_dict(self) -> dict:
        return json.loads(self.job_args)
