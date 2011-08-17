from django.db import models


class Dummy(models.Model):
    def __unicode__(self):
        return 'Dummy %s' % self.pk
