from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from datetime import datetime


from newsfeed.models import Article
from .models import ArticleImage


def images(request,article_id):
    article = get_object_or_404(Article,pk=article_id)
    images = ArticleImage.objects.filter(article__id=article_id)

    template = loader.get_template('outlets.html')
    context = {
        "images":images,
        "article":article
    }
    return HttpResponse(template.render(context,request))