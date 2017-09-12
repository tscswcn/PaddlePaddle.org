from django.template.loader import get_template
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings


def catch_all_handler(request, path=None):
    # Resolve path based on template.
    if path:
        # if '/' in path:
        #     return render(request, settings.CONTENT_DIR + '/' + path + '.html', {
        #         'path': path
        #     })
        # else:
        # Return the index of the app's documentation.

        # TODO: Test nested paths to make sure they pull correctly
        static_content_template = get_template(path + '/index.html')
        return render(request, '_base.html', {'static_content': static_content_template.render()})