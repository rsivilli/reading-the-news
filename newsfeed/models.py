from django.db import models


class NewsOutlet(models.Model):
    name = models.CharField(max_length=255, blank=False, unique=True)
    rss_url = models.CharField(max_length=255, blank=False)
    rss_last_scanned = models.DateTimeField(null=True, blank=True)
    article_class = models.CharField(max_length=255, blank=False)

    def __str__(self) -> str:
        return self.name


class Article(models.Model):
    url = models.CharField(max_length=510, blank=False, unique=True)
    title = models.CharField(max_length=255)
    publish_date = models.DateTimeField(null=False)
    scanned_date = models.DateTimeField(null=False)
    content = models.TextField()
    outlet = models.ForeignKey(NewsOutlet, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title
