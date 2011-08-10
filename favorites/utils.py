from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest


def get_object_or_400_response(app_label, object_name, object_id):
    """Try to fetch the described object, if it fails, returns a HttpResponse"""
    model = get_model(app_label, object_name)
    try:
        content_type = ContentType.objects.get_for_model(model)
    except AttributeError: # there no such model
        return HttpResponseBadRequest()
    else:
        try:
            instance = content_type.get_object_for_this_type(pk=object_id)
        except model.DoesNotExist: # there no such object
            return HttpResponseBadRequest()
        else:
            return instance
