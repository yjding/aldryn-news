# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse


class FormatableReverse(object):
    """Reverses view name at a time of string formatting.

    Trims the dict used to formatting to desired keys only.

    Usefull as a `redirect_to` `url` parameter. """

    def __init__(self, viewname, keys=None):
        self.viewname = viewname
        self.keys = keys

    def __mod__(self, kwargs):
        in_keys = lambda (x, y): x in self.keys
        kwargs = dict(filter(in_keys, kwargs.iteritems()))
        return reverse(self.viewname, kwargs=kwargs)
