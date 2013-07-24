# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from aldryn_news.menu import NewsCategoryMenu

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class NewsApp(CMSApp):
    name = _('News')
    urls = ['aldryn_news.urls']
    menus = [NewsCategoryMenu]

apphook_pool.register(NewsApp)
