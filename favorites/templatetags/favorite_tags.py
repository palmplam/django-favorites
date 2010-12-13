from django import template
from django.core.urlresolvers import reverse
from favorites.models import Favorite
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.filter
def is_favorite(object, user):
    """
    Returns True, if object is already in user`s favorite list
    """
    if not user or not user.is_authenticated():
        return False
    return Favorite.objects.favorites_for_object(object, user).count()>0


@register.inclusion_tag("favorites/favorite_add_remove.html")
def add_remove_favorite(object, user):
    favorite = None
    content_type = ContentType.objects.get_for_model(object)
    if user.is_authenticated():
        favorite = Favorite.objects.favorites_for_object(object, user=user)
        if favorite:
            favorite = favorite[0]
        else:
            favorite = None
    count = Favorite.objects.favorites_for_object(object).count()
            
    return {"object":object,
            "content_type": content_type,
            "user": user,
            "favorite":favorite,
            "count": count}
    
    
    
