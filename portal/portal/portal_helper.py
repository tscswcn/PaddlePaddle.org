from django.utils.translation import LANGUAGE_SESSION_KEY
from django.conf import settings


def get_preferred_version(request):
    """
    Observes the user's session to find the preferred documentation version.
    """
    return request.COOKIES.get(settings.PREFERRED_VERSION_NAME, settings.DEFAULT_DOCS_VERSION)


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
