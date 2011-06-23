from django.utils import unittest
from django.test import Client
from django.db import models
from django.contrib.auth.models import User

from models import Favorite
from models import Folder

from managers import FavoritesManagerMixin


class DummyModel(models.Model):
    pass


class BaseFavoritesTestCase(unittest.TestCase):
    def setUp(self):
        self.users = dict()
        for name in ['godzilla', 'leviathan']:
            u = User.objects.create(username=name)
            u.set_password(name)
            self.users[name] = u  # password is same as login
        self.client = Client(enforce_csrf_checks=True)


class FolderTests(BaseFavoritesTestCase):
    def setUp(self):
        super(FolderTests, self).setUp()

        godzilla = self.users['godzilla']

        Folder(name="foo", user=godzilla).save()
        Folder(name="bar", user=godzilla).save()


    def testFolders(self):
        reponse = self.client.login('godzilla')
        response = self.client.get('/folders')
        object_list = response.context['object_list']

        for folder in user_folders:
            self.assertTrue(folder.name in ['foo', 'bar'])


"""
class AnimalManager(models.Manager, FavoritesManagerMixin):
    pass


class Animal(models.Model):
    name = models.CharField(max_length=20)

    objects = AnimalManager()

    def __unicode__(self):
        return self.name

class FavoritesMixinTestCase(BaseFavoriteTestCase):
    def testWithFavorites(self):
        alice = self.users['alice']
        chris = self.users['chris']
        animals = {}
        for a in ['zebra', 'donkey', 'horse']:
            ani = Animal(name=a)
            ani.save()
            animals[a] = ani

        Favorite.objects.create_favorite(alice, animals['zebra'])
        Favorite.objects.create_favorite(chris, animals['donkey'])

        zebra = Animal.objects.with_favorite_for(alice).get(name='zebra')
        self.assertEquals(zebra.favorite__favorite, 1)

        all_animals = Animal.objects.with_favorite_for(alice).all()
        self.assertEquals(len(all_animals), 3)

        favorite_animals = Animal.objects.with_favorite_for(alice, all=False).all()
        self.assertEquals(len(favorite_animals), 1)
"""
