# -*- coding: utf-8 -*-
from django.utils.functional import SimpleLazyObject
try:
    from django.utils.functional import empty
except ImportError:
    # django 1.3 backwards compatibility
    empty = None

from django_geoip.base import current_location_storage_class


def get_location(request):
    from django_geoip.base import Locator
    if not hasattr(request, '_cached_location'):
        request._cached_location = Locator(request).locate()
    return request._cached_location


def get_current_location(request):
    from django_geoip.base import CurrentLocator
    if not hasattr(request, '_cached_current_location'):
        request._cached_current_location = CurrentLocator(request).locate()
    return request._cached_current_location


class LocationMiddleware(object):

    def process_request(self, request):
        """ Don't detect location, until we request it implicitly """
        request.location = SimpleLazyObject(lambda: get_location(request))
        request.current_location = SimpleLazyObject(
            lambda: get_current_location(request))

    def process_response(self, request, response):
        if hasattr(request, 'current_location') and \
           hasattr(request.current_location, '_wrapped'):
            if request.current_location._wrapped is empty:
                request.current_location._setup()
            scls = current_location_storage_class(request=request,
                                                  response=response)
            scls.set(location=request.current_location._wrapped)
        return response
