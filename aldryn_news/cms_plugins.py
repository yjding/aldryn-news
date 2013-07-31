# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from aldryn_news import models
from aldryn_news.forms import LatestNewsForm


class LatestNewsPlugin(CMSPluginBase):

    module = 'News'
    render_template = 'aldryn_news/plugins/latest_entries.html'
    name = _('Latest News Entries')
    model = models.LatestNewsPlugin
    form = LatestNewsForm

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context

plugin_pool.register_plugin(LatestNewsPlugin)
