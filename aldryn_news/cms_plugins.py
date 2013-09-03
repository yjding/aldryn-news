# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from aldryn_news import models
from aldryn_news.forms import MultipleTagForm, LinksForm


class NewsPluginBase(CMSPluginBase):

    module = 'News'


@plugin_pool.register_plugin
class LatestNewsPlugin(NewsPluginBase):

    render_template = 'aldryn_news/plugins/latest_entries.html'
    name = _('Latest News Entries')
    model = models.LatestNewsPlugin
    form = MultipleTagForm

    def render(self, context, instance, placeholder):
        context['FULL'] = models.LatestNewsPlugin.FULL
        context['SIMPLE'] = models.LatestNewsPlugin.SIMPLE
        context['instance'] = instance
        return context


@plugin_pool.register_plugin
class TagsPlugin(NewsPluginBase):

    render_template = 'aldryn_news/plugins/tags.html'
    name = _('Tags')
    form = MultipleTagForm

    def render(self, context, instance, placeholder):
        context['tags'] = models.News.published.get_tags(language=instance.language)
        return context


@plugin_pool.register_plugin
class ArchivePlugin(NewsPluginBase):

    render_template = 'aldryn_news/plugins/archive.html'
    name = _('Archive')

    def render(self, context, instance, placeholder):
        context['dates'] = models.News.published.get_months(language=instance.language)
        return context


@plugin_pool.register_plugin
class NewsLinksPlugin(NewsPluginBase):

    render_template = 'aldryn_news/plugins/news_links.html'
    name = _("News links")
    model = models.NewsLinksPlugin
    form = LinksForm
    filter_horizontal = ['news']

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context
