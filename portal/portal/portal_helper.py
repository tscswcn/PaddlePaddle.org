import os

from django.utils.translation import LANGUAGE_SESSION_KEY
from django.conf import settings


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
            folder_names.append(item)

    return folder_names


def folder_name_for_content_id(content_id):
    folder_name = None

    # TODO[Thuan]: Get this from configuration file
    if content_id:
        if content_id == 'documentation':
            folder_name = 'Paddle'
        elif content_id == 'book':
            folder_name = 'book'
        elif content_id == 'models':
            folder_name = 'models'

    return folder_name


def content_id_for_folder_name(folder_name):
    content_id = None

    # TODO[Thuan]: Get this from configuration file
    if folder_name:
        if folder_name == 'Paddle':
            content_id = 'documentation'
        elif folder_name == 'book':
            content_id = 'book'
        elif folder_name == 'models':
            content_id = 'models'

    return content_id