# -*- coding: utf-8 -*-
import datetime
from collections import Counter
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.core.exceptions import ImproperlyConfigured

from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.utils.translation import ugettext_lazy as _, override
from django.utils.timezone import now

from cms.utils.i18n import get_current_language
from cms.models.fields import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from taggit.models import (GenericTaggedItemBase as TaggitGenericTaggedItemBase,
                           ItemBase as TaggitItemBase)
from taggit.managers import TaggableManager
from hvad.models import TranslatableModel, TranslatedFields, TranslationManager
from hvad.utils import get_translation
from unidecode import unidecode


def get_slug_in_language(record, language):
    if not record:
        return None
    if hasattr(record, record._meta.translations_cache) and language == record.language_code:  # possibly no need to hit db, try cache
        return record.lazy_translation_getter('slug')
    else:  # hit db
        try:
            translation = get_translation(record, language_code=language)
        except models.ObjectDoesNotExist:
            return None
        else:
            return translation.slug


def get_page_url(name, language):
    try:
        url = reverse(name)
    except NoReverseMatch:
        error = _("There is no page translation for the language: %(lang)s"
                  % {'lang': language})
        raise ImproperlyConfigured(error)
    return url


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
        with override(language):
            if not slug:  # category not translated in given language
                try:
                    return get_page_url('latest-news', language)
                except ImproperlyConfigured:
                    return '/'

            kwargs = {'category_slug': slug}
            return reverse('news-category', kwargs=kwargs)


class TagManager(TranslationManager):

    def get_query_set(self):
        return self.language()


class Tag(TranslatableModel):

    translations = TranslatedFields(
        name=models.CharField(_('Name'), max_length=255),
        slug=models.SlugField(verbose_name=_('Slug'), max_length=100),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    objects = TagManager()

    def __unicode__(self):
        return self.name

    @classmethod
    def save_translations(cls, instance, **kwargs):
        opts = cls._meta
        if hasattr(instance, opts.translations_cache):
            trans = getattr(instance, opts.translations_cache)
            if not trans.master_id:
                trans.master = instance
                trans.slug = slugify(unidecode(trans.name))
            trans.save()


class TaggedItemBase(TaggitItemBase):

    tag = models.ForeignKey(Tag, related_name="%(app_label)s_%(class)s_items")

    class Meta:
        abstract = True

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()


class TaggedItem(TaggitGenericTaggedItemBase, TaggedItemBase):

    class Meta:
        verbose_name = _("Tagged Item")
        verbose_name_plural = _("Tagged Items")


class RelatedManager(TranslationManager):

    def using_translations(self):
        # not overriding get_queryset, as hvad doesn't use that
        qs = super(RelatedManager, self).using_translations()
        qs = qs.select_related('key_visual')
        # bug in hvad - Meta ordering isn't preserved
        qs = qs.order_by('-publication_start')
        return qs

    def get_tags(self, language, news_ids=None):
        """Returns tags used to tag news and its count. Results are ordered by count."""

        # get tagged news

        if not news_ids:
            news_ids = self.language(language).values_list('pk', flat=True)

        kwargs = {
            "object_id__in": set(news_ids),
            "content_type": ContentType.objects.get_for_model(self.model)
        }

        # aggregate and sort
        counted_tags = dict(TaggedItem.objects
                                      .filter(**kwargs)
                                      .values('tag')
                                      .annotate(count=models.Count('tag'))
                                      .values_list('tag', 'count'))

        # and finally get the results
        tags = Tag.objects.filter(pk__in=counted_tags.keys())
        for tag in tags:
            tag.count = counted_tags[tag.pk]
        return sorted(tags, key=lambda x: -x.count)

    def get_months(self, language):
        """Get months with aggregatet count (how much news is in the month). Results are ordered by date."""
        # done via naive way as django's having tough time while aggregating on date fields
        news = self.language(language)
        dates = news.values_list('publication_start', flat=True)
        dates = [(x.year, x.month) for x in dates]
        date_counter = Counter(dates)
        dates = set(dates)
        dates = sorted(dates, reverse=True)
        return [{'date': datetime.date(year=year, month=month, day=1),
                 'count': date_counter[year, month]} for year, month in dates]


class PublishedManager(RelatedManager):

    def using_translations(self):
        # not overriding get_queryset, as hvad doesn't use that
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
    tags = TaggableManager(blank=True, through=TaggedItem)

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ['-publication_start']

    def __unicode__(self):
        return self.lazy_translation_getter('title', str(self.pk))

    def get_absolute_url(self, language=None):
        language = language or get_current_language()
        slug = get_slug_in_language(self, language)
        with override(language):
            if not slug:   # news not translated in given language
                if self.category:
                    return self.category.get_absolute_url(language=language)

                try:
                    return get_page_url('latest-news', language)
                except ImproperlyConfigured:
                    return '/'

            kwargs = {
                'year': self.publication_start.year,
                'month': self.publication_start.month,
                'day': self.publication_start.day,
                'slug': slug
            }

            category_slug = get_slug_in_language(self.category, language)
            if category_slug:
                kwargs['category_slug'] = category_slug

            return reverse('news-detail', kwargs=kwargs)


class LatestNewsPlugin(CMSPlugin):

    FULL = 'full'
    SIMPLE = 'simple'

    TYPES = (
        (FULL, _("Full list")),
        (SIMPLE, _("Simple list")),
    )

    latest_entries = models.IntegerField(default=5, help_text=_('The number of latests entries to be displayed.'))
    type_list = models.CharField(verbose_name=_("Type of list"), choices=TYPES, default=FULL, max_length=255)
    tags = models.ManyToManyField('taggit.Tag', blank=True, help_text=_('Show only the news tagged with chosen tags.'))

    def __unicode__(self):
        return str(self.latest_entries)

    def copy_relations(self, oldinstance):
        self.tags = oldinstance.tags.all()

    def get_news(self):
        news = News.published.language(self.language).select_related('category')
        tags = list(self.tags.all())
        if tags:
            tagged_news = News.objects.filter(tags__in=tags)
            news = news.filter(id__in=tagged_news)
        return news[:self.latest_entries]


class NewsLinksPlugin(CMSPlugin):

    news = models.ManyToManyField(News, verbose_name=_("News"))

    def copy_relations(self, oldinstance):
        self.news = oldinstance.news.all()

    def get_news(self):
        return self.news.all()
