from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.template import loader
import json

from newsfeed.models import Article
from .models import ArticleImage, DreamJob, JobStatus, JobType

JOB_TYPE_KEY = "job_type"


def images(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    images = ArticleImage.objects.filter(article__id=article_id)

    template = loader.get_template("outlets.html")
    context = {"images": images, "article": article}
    return HttpResponse(template.render(context, request))


def generate_job(request: HttpRequest, article_id: int):
    article = get_object_or_404(Article, pk=article_id)
    query_dict = request.GET.copy()
    job_type = query_dict.get(JOB_TYPE_KEY, None)
    if job_type is None:
        return HttpResponse(
            dict(
                status_code=400,
                msg=f"{JOB_TYPE_KEY} query parameter is required",
            )
        )
    if job_type not in JobType.values:
        vals = ",".join(JobType.values)
        return HttpResponse(
            dict(
                status_code=400,
                msg=f"{JOB_TYPE_KEY} query parameter must be one of {vals}",
            )
        )
    query_dict.__delitem__(JOB_TYPE_KEY)

    job = DreamJob(
        article=article,
        job_status=JobStatus.QUEUED,
        job_type=job_type,
        job_args=json.dumps(query_dict),
    )
    job.save()

    return HttpResponse(dict(status_code=201))
