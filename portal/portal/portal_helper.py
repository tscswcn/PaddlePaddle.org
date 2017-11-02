import os

from django.utils.translation import LANGUAGE_SESSION_KEY
from django.conf import settings


CONTENT_ID_TO_FOLDER_MAP = {
    'documentation': 'Paddle',
    'models': 'models',
    'book': 'book',
    'mobile': 'Mobile'
}

# Invert the keys and value.  This assumes that the values are all unique
FOLDER_MAP_TO_CONTENT_ID = {v: k for k, v in CONTENT_ID_TO_FOLDER_MAP.iteritems()}

def get_preferred_version(request):
    """
    Observes the user's session to find the preferred documentation version.
    """
    preferred_version = request.COOKIES.get(settings.PREFERRED_VERSION_NAME, settings.DEFAULT_DOCS_VERSION)
    if settings.DOC_MODE:
        preferred_version = settings.DEFAULT_DOCS_VERSION

    return preferred_version


def set_preferred_version(request, response, preferred_version):
    """
    Sets the preferred documentation version in the user's session.
    """
    if preferred_version:
        if request:
            request.session[settings.PREFERRED_VERSION_NAME] = preferred_version

        if response:
            response.set_cookie(settings.PREFERRED_VERSION_NAME, preferred_version)

    request.session.modified = True


def get_preferred_language(request):
    """
    Observes the user's session, and consequently the cookies,
    to find the preferred documentation language.
    """
    preferred_lang = request.session.get(LANGUAGE_SESSION_KEY, None)
    if not preferred_lang:
        preferred_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME, 'en')

    return preferred_lang


def set_preferred_language(request, response, lang):
    """
    Sets the preferred documentation version in the user's session AND cookie.
    """
    request.session[LANGUAGE_SESSION_KEY] = lang
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
    request.session.modified = True


def get_available_doc_folder_names():
    folder_names = []

    root_path = '%s' % settings.CONTENT_DIR

    for item in os.listdir(root_path):
        if os.path.isdir(os.path.join(root_path, item)) and not item.startswith('.'):
            if item in CONTENT_ID_TO_FOLDER_MAP.values():
                # Only add folders that exists in our map
                folder_names.append(item)

    return folder_names


def folder_name_for_content_id(content_id):
    # TODO[Thuan]: Get this from configuration file
    return CONTENT_ID_TO_FOLDER_MAP.get(content_id, None)


def content_id_for_folder_name(folder_name):
    # TODO[Thuan]: Get this from configuration file
    return FOLDER_MAP_TO_CONTENT_ID.get(folder_name, None)