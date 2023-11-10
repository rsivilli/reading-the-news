from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from datetime import datetime


from .models import NewsOutlet,Article
from .tools.rss import get_feed, get_article

def news_outlets(request):
    outlets = NewsOutlet.objects.all().values()
    template = loader.get_template('outlets.html')
    context = {
        "outlets":outlets
    }
    return HttpResponse(template.render(context,request))

def articles(request,outlet_id:int):
    
    template = loader.get_template("articles.html")
    outlet = get_object_or_404(NewsOutlet,pk=outlet_id)
    articles = Article.objects.filter(outlet__id=outlet_id).all()
    context = {
        "articles":articles,
        "outlet": outlet
    }
    return HttpResponse(template.render(context,request))

    
def scan_rss(request, outlet_id:int):
    outlet = get_object_or_404(NewsOutlet,pk=outlet_id)

    for channel in get_feed(outlet.rss_url):
        for item in channel.items:
            if Article.objects.filter(url=item.link).first() is None:
                article = get_article(item.link,outlet.article_class)
                tmp = Article(
                    url = item.link,
                    title = item.title,
                    publish_date = item.pubDate,
                    scanned_date = datetime.utcnow(),
                    content = "\n".join(article.paragraphs),
                    outlet = outlet

                )
                tmp.save()
    outlet.rss_last_scanned = datetime.utcnow()
    outlet.save()
    return HttpResponse(dict(
        status_code = 200
    ))
            


    
    
