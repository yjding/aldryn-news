# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from aldryn_news import models
from aldryn_news.forms import MultipleTagForm


class NewsPluginBase(CMSPluginBase):

    module = 'News'


@plugin_pool.register_plugin
class LatestNewsPlugin(NewsPluginBase):

    render_template = 'aldryn_news/plugins/latest_entries.html'
    name = _('Latest News Entries')
    model = models.LatestNewsPlugin
    form = MultipleTagForm


@plugin_pool.register_plugin
class TagsPlugin(NewsPluginBase):

    render_template = 'aldryn_news/plugins/tags.html'
    name = _('Tags')
    model = models.TagsPlugin
    form = MultipleTagForm
