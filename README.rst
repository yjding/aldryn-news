===============
Aldryn News App
===============

Simple news application. It allows you to:

- write a tagable news
- plug in latest new messages (optionally filtered by tags)
- attach news archive view

Installation
============

Aldryn Platrofm Users
---------------------

Choose a site you want to install the add-on to from the dashboard. Then go to ``Apps -> Install app`` and click ``Install`` next to ``News`` app.

Redeploy the site.

Manuall Installation
--------------------

Run ``pip install aldryn-news``.

Add below apps to ``INSTALLED_APPS``: ::

    INSTALLED_APPS = [
        …
        'taggit',
        'aldryn_news',
        'aldryn_search',
        'django_select2',
        'djangocms_text_ckeditor',
        'easy_thumbnails',
        'filer',
        'hvad',
        'haystack', # for search
        …
    ]

Posting news
============

You can add news in the admin interface now. Search for the label ``Aldryn_News``.

In order to display them, create a CMS page and install the app there (choose ``News`` from the ``Advanced Settings -> Application`` dropdown).

Now redeploy the site again.

The above CMS site has become a news archive view.


Available Plug-ins
==================

``Latest News Entries`` plugin lets you list **n** most frequent news filtered by tags.


Search
==================

By default, the news entries are searchable using ``django-haystack``.

You can turn it this behavior off by setting ``ALDRYN_NEWS_SEARCH = False`` in your django settings.