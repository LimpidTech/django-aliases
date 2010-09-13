from django.db.models import Manager
from django.contrib import contenttypes
import models

class URLManager(models.Manager):
    def related_to(self, obj):
        content_type = contenttypes.models.ContentType.get_object_for_this_type(models.URL)
        return super(URLManager, self).get_query_set().filter(content_type=content_type, object_id=obj.pk)

