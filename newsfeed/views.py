from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from django.core.paginator import Paginator
from dataclasses import dataclass

from dreamer.models import ArticleImage, ArticleAudio, ArticleVideo
from .models import NewsOutlet, Article
from .tools.rss import get_feed, get_article


@dataclass
class ParagraphView:
    content: str
    audio: ArticleAudio | None = None
    image: ArticleImage | None = None


def outlet_detail(request, outlet_id: int):
    template = loader.get_template("outlet_detail.html")
    print(template)
    outlet = get_object_or_404(NewsOutlet, pk=outlet_id)

    articles = Paginator(
        Article.objects.filter(outlet__id=outlet_id)
        .order_by("-publish_date")
        .all(),
        10,
    )

    page_number = request.GET.get("page")
    page_obj = articles.get_page(page_number)

    context = {
        "outlet": outlet,
        "articles": page_obj,
    }
    return HttpResponse(template.render(context, request))


def article_detail(request, article_id: int):
    template = loader.get_template("article_detail.html")
    article = get_object_or_404(Article, pk=article_id)
    images = list(
        ArticleImage.objects.filter(article__id=article_id)
        .order_by("paragraph_number")
        .all()
    )
    audio = list(
        ArticleAudio.objects.filter(article__id=article_id)
        .order_by("paragraph_number")
        .all()
    )
    video = ArticleVideo.objects.filter(article__id=article_id).first()
    paragraph_views: list[ParagraphView] = []

    for aud in audio:
        aud.location = "/" + aud.location
    for img in images:
        img.image_location = "/" + "/".join(img.image_location.split("/")[-2:])
    if video:
        video.location = "/" + video.location
    paragraphs = article.content.split("\n")
    for i in range(len(paragraphs)):
        tmp = ParagraphView(content=paragraphs[i])
        if images and images[0].paragraph_number == i:
            tmp.image = images.pop(0)
        if audio and audio[0].paragraph_number == i:
            tmp.audio = audio.pop(0)
        paragraph_views.append(tmp)

    print(video)
    context = {
        "article": article,
        "paragraphs": paragraph_views,
        "video": video,
    }
    return HttpResponse(template.render(context, request))


def news_outlets(request):
    outlets = NewsOutlet.objects.all().values()
    template = loader.get_template("outlets.html")
    context = {"outlets": outlets}
    return HttpResponse(template.render(context, request))


def articles(request, outlet_id: int):
    template = loader.get_template("articles.html")
    outlet = get_object_or_404(NewsOutlet, pk=outlet_id)
    articles = Paginator(
        Article.objects.filter(outlet__id=outlet_id).all(), 10
    )
    context = {"articles": articles, "outlet": outlet}
    return HttpResponse(template.render(context, request))


def scan_rss(request, outlet_id: int):
    outlet = get_object_or_404(NewsOutlet, pk=outlet_id)

    for channel in get_feed(outlet.rss_url):
        for item in channel.items:
            if Article.objects.filter(url=item.link).first() is None:
                article = get_article(item.link, outlet.article_class)
                tmp = Article(
                    url=item.link,
                    title=item.title,
                    publish_date=item.pubDate,
                    scanned_date=datetime.utcnow(),
                    content="\n".join(article.paragraphs),
                    outlet=outlet,
                )
                tmp.save()
    outlet.rss_last_scanned = datetime.utcnow()
    outlet.save()
    return HttpResponse(dict(status_code=200))
