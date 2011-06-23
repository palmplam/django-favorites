from django.db import models, connection
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from favorites.managers import FavoriteManager


class Folder(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    folder = models.ForeignKey(Folder, null=True)

    created_on = models.DateTimeField(auto_now_add=True)

    objects = FavoriteManager()

    class Meta:
        verbose_name = _('favorite')
        verbose_name_plural = _('favorites')
        unique_together = (('user', 'content_type', 'object_id'),)

    def __unicode__(self):
        object_repr = unicode(self.content_object)
        return u"%s likes %s" % (self.user, object_repr)


def remove_favorites(sender, **kwargs):
    instance = kwargs.get('instance')
    # Solves the session pk issue.
    if isinstance(instance.pk, int):
        Favorite.objects.favorites_for_object(instance).delete()

models.signals.post_delete.connect(remove_favorites)
