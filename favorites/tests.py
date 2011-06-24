from django.db import models
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from django.db import models

from models import Favorite
from models import Folder
from managers import FavoritesManagerMixin


class DummyModel(models.Model):
    pass

class BaseFavoriteTestCase(TestCase):
    urls = 'favorites.urls'

    def setUp(self):
        self.users = dict([(u.username, u) for u in User.objects.all()])
        if len(self.users) != 4:
            for name in ['alice', 'bob', 'chris', 'dawn']:
                try:
                    u = User.objects.create(username=name)
                    self.users[name] = u
                except:
                    pass

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

    def setUp(self):
        pass

    def tearDown(self):
        self.client.logout()


    def user(self, name):
        user = User(username=name)
        user.set_password(name)
        user.save()
        return user


class DeleteFavoriteTests(BaseFavoriteTestCase):
    """Tests for delete-favorite url"""
    def test_login_required(self):
        """The user should be logged in to be able to delete a
        favorite."""
        response = self.client.post('/favorite/delete/')
        self.assertEquals(response.status_code, 302)

    def test_get_fails(self):
        """GET method is not available."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/favorite/delete/')
        self.assertEquals(response.status_code, 400)
        godzilla.delete()

    def test_submit(self):
        """Submit a valid form."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        response = self.client.post('/favorite/delete/',
                                    {'object_id': favorite.pk})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(Favorite.objects.all()), 0)
        favorite.delete()
        godzilla.delete()

    def test_delete_invalid_object(self):
        """Submit an invalid form, should raise a 404 error page since
        the object does not exists"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.post('/favorite/delete/',
                                    {'object_id': 1})
        self.assertEquals(response.status_code, 404)
        godzilla.delete()
        

    def test_delete_invalid_user(self):
        """It shouldn't be possible for user to delete a favorite
        of another user"""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, leviathan)
        response = self.client.post('/favorite/delete/',
                                    {'object_id': favorite.pk})
        self.assertEquals(response.status_code, 403)
        favorite.delete()
        godzilla.delete()
    

class MoveFavoriteTests(BaseFavoriteTestCase):
    """Tests for move-favorite url"""
    def test_login_required_get(self):
        response = self.client.get('/favorite/move/1')
        self.assertEquals(response.status_code, 302)
        
    def test_login_required_post(self):
        response = self.client.post('/favorite/move/1')
        self.assertEquals(response.status_code, 302)

    def test_render_form(self):
        """a GET request will return a form, with the object that match
        the object_id in url and a list of the user folder's"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        folders = []
        for i in range(10):
            folder = Folder(name="folder-%s" % i, user=godzilla)
            folder.save()
            folders.append(folder)
        response = self.client.get('/favorite/move/%s' % favorite.pk)
        self.assertEquals(response.status_code, 200)

        user_folders = [(0, '')]
        user_folders.extend(Folder.objects.filter(user=godzilla).order_by('name').values_list('pk', 'name'))

        for option in user_folders:
            choices = response.context['form'].fields['folder'].choices
            self.assertIn(option, choices)

        object = response.context['object']
        self.assertEquals(object.pk, favorite.pk)
        favorite.delete()
        godzilla.delete()
        for folder in folders:
            folder.delete()
        dummy.delete()         
    
    def test_object_does_exists(self):
        """If the object does not exists the server
        should return a 404"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/favorite/move/1')
        self.assertEquals(response.status_code, 404)
        godzilla.delete()        

    def test_invalid_user(self):
        """If the user is not the owner of the object,
        the server should answer a 403 error"""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, leviathan)
        response = self.client.get('/favorite/move/%s' % favorite.pk)
        self.assertEquals(response.status_code, 403)
        favorite.delete()
        godzilla.delete()
        leviathan.delete()
        dummy.delete()

    def test_submit(self):
        """All is for the best in the best of all possible worlds."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        folder = Folder(name="japan", user=godzilla)
        folder.save()
        response = self.client.post('/favorite/move/%s' % favorite.pk, 
                                    {'object_id': favorite.pk, 'folder': folder.pk})
        self.assertEquals(response.status_code, 302)
        object = Favorite.objects.get(pk=favorite.pk)
        self.assertEqual(folder.pk, object.folder.pk)
        folder.delete()
        favorite.delete()
        godzilla.delete()
        dummy.delete()

    def test_submit_invalid(self):
        """If the user try to move an object to a folder owned 
        by another user the server should show the form again. It handles
        cases where the user provide a complete invalid folder id."""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        folder = Folder(name="china", user=leviathan)
        folder.save()
        response = self.client.post('/favorite/move/%s' % favorite.pk, 
                                    {'object_id': favorite.pk, 'folder': folder.pk})
        self.assertEquals(response.status_code, 200)
        folder.delete()
        favorite.delete()
        godzilla.delete()
        leviathan.delete()
        dummy.delete()

    def test_submit_unknown_folder(self):
        """If the user try to move an object to a folder that
        doesn't exists the server should answer with a 404 error."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        response = self.client.post('/favorite/move/%s' % favorite.pk, 
                                    {'object_id': favorite.pk, 'folder': 1})
        self.assertEquals(response.status_code, 200)
        favorite.delete()
        godzilla.delete()
        dummy.delete()

    def test_submit_move_to_root(self):
        """It should be possible to move an object to root folder,
        when the user select the empty option (the key is 0)"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        response = self.client.post('/favorite/move/%s' % favorite.pk, 
                                    {'object_id': favorite.pk, 'folder': 0})
        self.assertEquals(response.status_code, 302)
        object = Favorite.objects.get(pk=favorite.pk)
        self.assertIsNone(object.folder)
        favorite.delete()
        godzilla.delete()
        dummy.delete()

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
