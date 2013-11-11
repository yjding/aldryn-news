# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import RequestContext

from aldryn_search.base import AldrynIndexBase
from aldryn_search.utils import strip_tags

from aldryn_news.models import News


class NewsIndex(AldrynIndexBase):
    haystack_use_for_indexing = getattr(settings, "ALDRYN_NEWS_SEARCH", True)

    INDEX_TITLE = True

    def get_title(self, obj):
        return obj.title

    def get_index_kwargs(self, language):
        return {'translations__language_code': language}

    def get_index_queryset(self, language):
        return self.get_model().published.all()

    def get_model(self):
        return News

    def get_search_data(self, obj, language, request):
        text = strip_tags(obj.lead_in)
        plugins = obj.content.cmsplugin_set.filter(language=language)
        for base_plugin in plugins:
            instance, plugin_type = base_plugin.get_plugin_instance()
            if instance is None:
                # this is an empty plugin
                continue
            else:
                text += strip_tags(instance.render_plugin(context=RequestContext(request))) + u' '
        return text
