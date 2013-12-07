# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.utils.translation import get_language

from cms.utils import get_language_from_request

from aldryn_news.models import News


register = template.Library()


def get_language_from_context(context):
    if 'LANGUAGE_CODE' in context:
        return context['LANGUAGE_CODE']
    elif 'request' in context:
        return get_language_from_request(context['request'])
    else:
        return get_language() or settings.LANGUAGE_CODE


@register.assignment_tag(name='news_tags', takes_context=True)
def get_news_tags(context, news_list_name='object_list'):
    news_list = context.get(news_list_name)

    current_language = get_language_from_context(context)

    if news_list:
        news_ids = [news.pk for news in news_list]
        news_tags = News.published.get_tags(language=current_language, news_ids=news_ids)
        return news_tags
    return ''
