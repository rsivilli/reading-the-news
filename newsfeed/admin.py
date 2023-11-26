from django.contrib import admin
from .models import Article, NewsOutlet

# Register your models here.

admin.site.register(NewsOutlet)
admin.site.register(Article)
