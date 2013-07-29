# -*- coding: utf-8 -*-
import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from cms.utils.i18n import force_language, get_current_language
from cms.models.fields import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from taggit.managers import TaggableManager
from hvad.models import TranslatableModel, TranslatedFields, TranslationManager
from hvad.utils import get_translation


def get_slug_in_language(record, language):
    if not record:
        return None
    if language == record.language_code:  # possibly no need to hit db, try cache
        return record.lazy_translation_getter('slug')
    else:  # hit db
        try:
            translation = get_translation(record, language_code=language)
        except models.ObjectDoesNotExist:
            return None
        else:
            return translation.slug


class Category(TranslatableModel):

    translations = TranslatedFields(
        name=models.CharField(_('Name'), max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255, blank=True,
                              help_text=_('Auto-generated. Clean it to have it re-created. '
                                          'WARNING! Used in the URL. If changed, the URL will change. ')),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    ordering = models.IntegerField(_('Ordering'), default=0)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['ordering']

    def __unicode__(self):
        return self.lazy_translation_getter('name', str(self.pk))

    def get_absolute_url(self, language=None):
        language = language or get_current_language()
        slug = get_slug_in_language(self, language)
        with force_language(language):
            if not slug:  # category not translated in given language
                return reverse('latest-news')
            kwargs = {'category_slug': slug}
            return reverse('news-category', kwargs=kwargs)


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
        slug=models.CharField(_('Slug'), max_length=255, blank=True,
                              help_text=_('Auto-generated. Clean it to have it re-created. '
                                          'WARNING! Used in the URL. If changed, the URL will change. ')),
        lead_in=HTMLField(_('Lead-in'),
                          help_text=_('Will be displayed in lists, and at the start of the detail page')),
        meta={'unique_together': [['slug', 'language_code']]}
    )
    key_visual = FilerImageField(verbose_name=_('Key Visual'), blank=True, null=True)
    content = PlaceholderField('blog_post_content')
    publication_start = models.DateTimeField(_('Published Since'), default=datetime.datetime.now,
                                             help_text=_('Used in the URL. If changed, the URL will change.'))
    publication_end = models.DateTimeField(_('Published Until'), null=True, blank=True)
    category = models.ForeignKey(Category, verbose_name=_('Category'), blank=True, null=True,
                                 help_text=_('WARNING! Used in the URL. If changed, the URL will change.'))
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
        language = language or get_current_language()
        slug = get_slug_in_language(self, language)
        with force_language(language):
            if not slug:  # news not translated in given language
                if self.category:
                    return self.category.get_absolute_url(language=language)
                else:
                    return reverse('latest-news')
            kwargs = {'year': self.publication_start.year,
                      'month': self.publication_start.month,
                      'day': self.publication_start.day,
                      'slug': slug}
            category_slug = get_slug_in_language(self.category, language)
            if category_slug:
                kwargs['category_slug'] = category_slug
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
