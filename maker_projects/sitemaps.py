from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import MakerProject


class ProjectSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return MakerProject.objects.all()

    def lastmod(self, obj):
        return obj.created_at


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    protocol = "https"

    def items(self):
        return ["public_feed:home"]

    def location(self, item):
        return reverse(item)
