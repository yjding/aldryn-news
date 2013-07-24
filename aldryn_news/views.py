# -*- coding: utf-8 -*-
import datetime

from django.views.generic.dates import ArchiveIndexView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from aldryn_news.models import News

from menus.utils import set_language_changer


class BaseNewsView(object):

    def get_queryset(self):
        if self.request.user.is_staff:
            manager = News.objects
        else:
            manager = News.published
        return manager.language()


class ArchiveView(BaseNewsView, ArchiveIndexView):

    date_field = 'publication_start'
    allow_empty = True
    allow_future = True
    template_name = 'aldryn_news/news_archive.html'

    def get_queryset(self):
        qs = super(ArchiveView, self).get_queryset()
        if 'month' in self.kwargs:
            qs = qs.filter(publication_start__month=self.kwargs['month'])
        if 'year' in self.kwargs:
            qs = qs.filter(publication_start__year=self.kwargs['year'])
        return qs

    def get_context_data(self, **kwargs):
        kwargs['month'] = int(self.kwargs.get('month')) if 'month' in self.kwargs else None
        kwargs['year'] = int(self.kwargs.get('year')) if 'year' in self.kwargs else None
        if kwargs['year']:
            kwargs['archive_date'] = datetime.date(kwargs['year'], kwargs['month'] or 1, 1)
        return super(ArchiveView, self).get_context_data(**kwargs)


class TaggedListView(BaseNewsView, ListView):

    template_name = 'aldryn_news/news_list.html'

    def get_queryset(self):
        qs = super(TaggedListView, self).get_queryset()
        return qs.filter(tags__slug=self.kwargs['tag'])


class NewsDetailView(BaseNewsView, DetailView):

    template_name = 'aldryn_news/news_detail.html'

    def get_object(self):
        # django-hvad 0.3.0 doesn't support Q conditions in `get` method
        # https://github.com/KristianOellegaard/django-hvad/issues/119
        qs = self.get_queryset()
        qs.filter(slug=self.kwargs['slug'])
        return qs[0]

    def get(self, *args, **kwargs):
        response = super(NewsDetailView, self).get(*args, **kwargs)
        set_language_changer(self.request, self.object.get_absolute_url)
        return response
