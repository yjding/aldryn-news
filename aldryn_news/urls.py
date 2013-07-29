# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from aldryn_news.views import ArchiveView, CategoryListView, NewsDetailView, TaggedListView
from aldryn_news.feeds import CategoryFeed, LatestEntriesFeed, TagFeed

urlpatterns = patterns('',
    url(r'^$', ArchiveView.as_view(), name='latest-news'),
    url(r'^feed/$', LatestEntriesFeed(), name='latest-news-feed'),
    url(r'^tagged/(?P<tag>[-\w]+)/$', TaggedListView.as_view(), name='tagged-news'),
    url(r'^tagged/(?P<tag>[-\w]+)/feed/$', TagFeed(), name='tagged-news-feed'),
    url(r'^(?P<year>\d{4})/$', ArchiveView.as_view(), name='archive-year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', ArchiveView.as_view(), name='archive-month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]*)/$', NewsDetailView.as_view(), name='news-detail'),
    url(r'^(?P<category_slug>[-\w]+)/$', CategoryListView.as_view(), name='news-category'),
    url(r'^(?P<category_slug>[-\w]+)/feed/$', CategoryFeed(), name='news-category-feed'),
    url(r'^(?P<category_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]*)/$', NewsDetailView.as_view(), name='news-detail'),
)
