from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.template.loader import render_to_string
from exceptions import IndexError
from models import URL
import operator, re


raw_query = render_to_string('aliases/location_match.sql', {})


class AliasFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        try:
            if hasattr(settings, 'ALIASES_MAP_ARGS') and settings.ALIASES_MAP_ARGS is False:
                alias = URL.objects.get(location=request.path_info)
            else:
                params = (
                    request.path_info,
                )

                # I'm not a fan of raw SQL queries, but that's the only option.
                # If you know how to do this in django's ORM, let me know. If
                # this doesn't work and/or you don't need this functionality,
                # you can always set settings.ALIASES_MAP_ARGS to False and
                # avoid this. Alternatively, if you feel like hacking a bit
                # you can override the `aliases/location_match.sql` template
                # to do whatever you prefer in your SQL backend.
                alias = URL.objects.raw(raw_query, params)

                try:
                    alias = alias[0]
                except IndexError:
                    return response

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

