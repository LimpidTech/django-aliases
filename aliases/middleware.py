from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from exceptions import IndexError
from models import URL
import operator, re

class AliasFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        try:
            if hasattr(settings, 'ALIASES_MAP_ARGS') and settings.ALIASES_MAP_ARGS is False:
                alias = URL.objects.get(location=request.path_info)
            else:
                # I'm not a fan of raw SQL queries, but this should work in any
                # SQL server (I think). If you know how to do this in django's
                # ORM, let me know. If this doesn't work and/or you don't need
                # this functionality, you can always set
                # settings.ALIASES_MAP_ARGS to False and avoid this.
                #
                # This will not work in SQLite.

                alias = URL.objects.raw('SELECT * FROM aliases_url WHERE location LIKE "%s%%" ORDER BY LENGTH(location) DESC LIMIT 1', [request.path_info])

                try:
                    alias = alias[0]
                except IndexError:
                    alias = None

            if alias is not None:
                if alias.get_related_url():
                    try:
                        match = resolve(alias.get_related_url())
                    except Resolver404:
                        match = None
                else:
                    match = None

                # When we have extra data in the request, we pass it as args to the view
                if len(alias.location) < len(request.path_info):
                    additional_args = re.sub('\/$', '', request.path_info)
                    additional_args = additional_args[len(alias.location):].split('/')

                    # This is a tuple, which is immutable. Convert it to a list.
                    match.args = list(match.args)

                    match.args.extend(additional_args)

                if match:
                    return match.func(request, *match.args, **match.kwargs)
                else:
                    return HttpResponseRedirect(alias.get_related_url())
            else:
                raise Http404('The specified URL mapping does not exist.')

        except URL.DoesNotExist:
            return response

        except:
            if settings.DEBUG:
                raise

            return response

