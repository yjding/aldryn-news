# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool

from aldryn_news import request_news_identifier


@toolbar_pool.register
class NewsToolbar(CMSToolbar):

    def populate(self):
        def can(action, model):
            perm = 'aldryn_news.%(action)s_%(model)s' % {'action': action, 'model': model}
            return self.request.user.has_perm(perm)

        if can('add', 'news') or can('change', 'news'):
            menu = self.toolbar.get_or_create_menu('news-app', _('News'))
            if can('add', 'news'):
                menu.add_modal_item(_('Add News'), reverse('admin:aldryn_news_news_add') + '?_popup')

            job_offer = getattr(self.request, request_news_identifier, None)
            if job_offer and can('change', 'news'):
                url = reverse('admin:aldryn_news_news_change', args=(job_offer.pk,)) + '?_popup'
                menu.add_modal_item(_('Edit News'), url, active=True)
