from django.db import models
from newsfeed.models import Article
# Create your models here.
class ArticleImage(models.Model):
    image_location = models.CharField(max_length=255,null=False,blank=False)
    paragraph_number = models.SmallIntegerField(blank=False,null=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

class ArticleAudio(models.Model):
    location = models.CharField(max_length=255,null=False,blank=False)
    paragraph_number = models.SmallIntegerField(blank=False,null=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

class ArticleVideo(models.Model):
    location = models.CharField(max_length=255,null=False,blank=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)