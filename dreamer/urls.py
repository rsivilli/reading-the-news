from django.urls import path
from . import views

urlpatterns = [
    path("articles/<int:article_id>/images", views.images, name="images")
]
