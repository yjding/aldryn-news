# -*- coding: utf-8 -*-
from django.shortcuts import redirect

def redirect_to_viewname(request, viewname, keys, **kwargs):
    in_keys = lambda (x, y): x in keys
    kwargs = dict(filter(in_keys, kwargs.iteritems()))
    return redirect(viewname, **kwargs)
