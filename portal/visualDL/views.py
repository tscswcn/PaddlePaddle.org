# -*- coding: utf-8 -*-
import urllib

from django.shortcuts import render, redirect
from portal import portal_helper


def home_root(request):
    current_lang_code = request.LANGUAGE_CODE

    # Since we default to english, we set the change lang toggle to chinese
    lang_label = u'中文'
    lang_link = '/change-lang?lang_code=zh'

    if current_lang_code and current_lang_code == 'zh':
        lang_label = 'English'
        lang_link = '/change-lang?lang_code=en'

    context = {
        'lang_def': { 'label': lang_label, 'link': lang_link }
    }

    return render(request, 'visualdl/index.html', context)


def change_lang(request):
    """
    Change current documentation language.
    """
    lang = request.GET.get('lang_code', 'en')

    response = redirect('/')
    portal_helper.set_preferred_language(request, response, lang)

    return response