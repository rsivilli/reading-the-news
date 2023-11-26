from django.urls import path
from . import views

urlpatterns = [
    path("outlets/", views.news_outlets, name="outlets"),
    path(
        "outlets/<int:outlet_id>", views.outlet_detail, name="outletdetailed"
    ),
    path("outlets/<int:outlet_id>/scan", views.scan_rss, name="scan"),
    path("outlets/<int:outlet_id>/articles", views.articles, name="articles"),
    path("articles/<int:article_id>", views.article_detail, name="article"),
]
