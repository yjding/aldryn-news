# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap

from ..models import Category, News


class NewsCategoriesSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Category.objects.all()


class NewsSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return News.published.all()

    def lastmod(self, obj):
        return obj.publication_start
