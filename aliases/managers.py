from django.db.models import Manager
from django.contrib import contenttypes

class URLManager(Manager):
    def related_to(self, obj):
        content_type = contenttypes.models.ContentType.objects.get_for_model(obj.model_class())
        return super(URLManager, self).get_query_set().filter(content_type=content_type, object_id=obj.pk)

