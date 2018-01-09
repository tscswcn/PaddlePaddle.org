import os

class SubdomainMiddleware ():
    def process_request(self, request):

        # For requests within visualdl sub-domain, have the visualDL's urls.py to handle routing.
        host = request.META['HTTP_HOST']
        if host.startswith('visualdl.paddlepaddle.'):
            request.urlconf = 'visualDL.urls'

        return None
