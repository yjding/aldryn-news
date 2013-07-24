# -*- coding: utf-8 -*-
from django import forms

import django_select2
from hvad.forms import TranslatableModelForm
import taggit


class LatestNewsForm(forms.ModelForm):

    class Meta:
        widgets = {
            'tags': django_select2.Select2MultipleWidget
        }


class NewsTagWidget(django_select2.widgets.Select2Mixin, taggit.forms.TagWidget):

    def __init__(self, *args, **kwargs):
        options = kwargs.get('select2_options', {})
        options['tags'] = list(taggit.models.Tag.objects.values_list('name', flat=True))
        options['tokenSeparators'] = [' ', ',']
        kwargs['select2_options'] = options
        super(NewsTagWidget, self).__init__(*args, **kwargs)

    def render_js_code(self, *args, **kwargs):
        js_code = super(NewsTagWidget, self).render_js_code(*args, **kwargs)
        return js_code.replace('$', 'jQuery')


class NewsForm(TranslatableModelForm):

    class Meta:
        widgets = {
            'tags': NewsTagWidget
        }


class CategoryForm(TranslatableModelForm):

    class Meta:
        fields = ['name', 'slug']
