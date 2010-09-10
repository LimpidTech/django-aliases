from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from django.core.urlresolvers import resolve
from models import URL

class AliasFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        try:
            alias = URL.objects.get(location=request.path_info)

            if alias.get_related_url():
                match = resolve(alias.get_related_url())
            else:
                match = None

            if match:
                return match.func(request, *match.args, **match.kwargs)
            else:
                return HttpResponseRedirect(alias.get_related_url())

        except URL.DoesNotExist:
            return response

        except:
            if settings.DEBUG:
                raise

            return response

