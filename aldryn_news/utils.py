# -*- coding: utf-8 -*-
from django.shortcuts import redirect


def redirect_to_viewname(request, viewname, keys, **kwargs):
    kwargs = dict((x, y) for x, y in kwargs.iteritems() if x in keys)
    return redirect(viewname, **kwargs)
