# -*- coding: utf-8 -*-
import datetime
from collections import Counter

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from hvad.models import TranslationManager

from taggit.models import Tag, TaggedItem


class CategoryManager(TranslationManager):

    def get_with_usage_count(self, language=None, news_ids=None, **kwargs):
        if not news_ids:
            news_ids = self.language(language).values_list('pk', flat=True)

        kwargs['news__in'] = news_ids

        categories = list(self.language(language).filter(**kwargs).distinct())

        # No annotate in hvad.
        for category in categories:
            category.news_count = category.news_set.count()
        return sorted(categories, key=lambda x: -x.news_count)


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
        qs = qs.filter(publication_start__lte=timezone.now())
        qs = qs.filter(models.Q(publication_end__isnull=True) | models.Q(publication_end__gte=timezone.now()))
        return qs


class TagManager(TranslationManager):

    def get_query_set(self):
        return self.language()
