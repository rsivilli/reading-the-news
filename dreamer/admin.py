from django.contrib import admin
from .models import ArticleImage, ArticleAudio, ArticleVideo
# Register your models here.
admin.site.register(ArticleImage)
admin.site.register(ArticleAudio)
admin.site.register(ArticleVideo)
