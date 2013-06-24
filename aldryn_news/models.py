# -*- coding: utf-8 -*-
import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now


from cms.models.fields import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from taggit.managers import TaggableManager
from hvad.models import TranslatableModel, TranslatedFields, TranslationManager


class RelatedManager(TranslationManager):

    def using_translations(self):
        qs = super(RelatedManager, self).using_translations()
        qs = qs.select_related('key_visual')
        # bug in hvad - Meta ordering isn't preserved
        qs = qs.order_by('-publication_start')
        return qs


class PublishedManager(RelatedManager):

    def using_translations(self):
        qs = super(PublishedManager, self).using_translations()
        qs = qs.filter(publication_start__lte=now())
        qs = qs.filter(models.Q(publication_end__isnull=True) | models.Q(publication_end__gte=now()))
        return qs


class News(TranslatableModel):

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        slug=models.CharField(_('Slug'), max_length=255, unique=True, blank=True,
                              help_text=_('Used in the URL. If changed, the URL will change. ')),
        lead_in=HTMLField(_('Lead-in'),
                          help_text=_('Will be displayed in lists, and at the start of the detail page'))
    )
    key_visual = FilerImageField(verbose_name=_('Key Visual'), blank=True, null=True)
    content = PlaceholderField('blog_post_content')
    publication_start = models.DateTimeField(_('Published Since'), default=datetime.datetime.now,
                                             help_text=_('Used in the URL. If changed, the URL will change.'))
    publication_end = models.DateTimeField(_('Published Until'), null=True, blank=True)

    objects = RelatedManager()
    published = PublishedManager()
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ['-publication_start']

    def __unicode__(self):
        return self.lazy_translation_getter('title', str(self.pk))

    def get_absolute_url(self, language=None):
        if language:
            translation = self.__class__.objects.language(language_code=language).get(pk=self.pk)
        else:
            translation = self
        kwargs = {'year': self.publication_start.year,
                  'month': self.publication_start.month,
                  'day': self.publication_start.day,
                  'slug': translation.lazy_translation_getter('slug', str(self.pk))}
        return reverse('news-detail', kwargs=kwargs)


class LatestNewsPlugin(CMSPlugin):

    latest_entries = models.IntegerField(default=5, help_text=_('The number of latests entries to be displayed.'))
    tags = models.ManyToManyField('taggit.Tag', blank=True, help_text=_('Show only the news tagged with chosen tags.'))

    def __unicode__(self):
        return str(self.latest_entries)

    def copy_relations(self, oldinstance):
        self.tags = oldinstance.tags.all()

    def get_news(self):
        news = News.published.language(self.language)
        tags = list(self.tags.all())
        if tags:
            news = news.filter(tags__in=tags)
        return news[:self.latest_entries]
