from django.test import TestCase
from django.test import Client
from django.db import models
from django.contrib.auth.models import User

from models import Favorite
from models import Folder

from managers import FavoritesManagerMixin


class DummyModel(models.Model):
    pass


class BaseFavoritesTestCase(TestCase):
    urls = 'favorites.urls'

    def setUp(self):
        pass

    def tearDown(self):
        self.client.logout()

    def user(self, name):
        u = User.objects.create(username=name)
        u.set_password(name)
        u.save()
        return u


class FolderTests(BaseFavoritesTestCase):
    def test_folders(self):
        godzilla = self.user('godzilla')

        Folder(name="foo", user=godzilla).save()
        Folder(name="bar", user=godzilla).save()

        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/folders/')

        for folder in response.context['object_list']:
            self.assertIn(folder.name, ['foo', 'bar'])
        godzilla.delete()

    def test_folders_empty(self):
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')

        Folder(name="foo", user=godzilla).save()
        Folder(name="bar", user=godzilla).save()

        self.client.login(username='leviathan', password='leviathan')
        response = self.client.get('/folders/')
        self.assertEquals(len(response.context['object_list']), 0)

        Folder.objects.all().delete()
        godzilla.delete()

    def test_check_credentials(self):
        response = self.client.get('/folders/')
        self.assertEquals(response.status_code, 302)


class FolderAddTests(BaseFavoritesTestCase):
    def test_page_add(self):
        """A logged in user try to fetch the formular, should
        return a 200 page"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/folder/add/')
        self.assertEquals(response.status_code, 200)
        godzilla.delete()

    def page_check_credentials(self):
        """Not logged user haven't access to this page,
        should return a redirect"""
        response = self.client.get('/folder/add/')
        self.assertEquals(response.status_code, 302)

    def page_check_post(self):
        """A logged in user try to add a new folder,
        should return a redirect"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/folder/add/', {'name': 'japan'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Folder.objects.favorites_for_user(user).count(), 1)
        Folder.objects.all().delete()
        godzilla.delete()


class FolderDeleteTests(BaseFavoritesTestCase):
    def test_delete(self):
        """If you submit the form with empty object_id it should
        answer with 400 error"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/folder/delete/')
        self.assertEquals(response.status_code, 400)
        godzilla.delete()

    def test_check_credentials(self):
        """The user should be logged in to delete something"""
        response = self.client.get('/folder/delete/')
        self.assertEquals(response.status_code, 302)

    def test_delete_post(self):
        """Submit a delete request with good credential should
        answer a redirect"""
        godzilla = self.user('godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.post('/folder/delete/', {'object_id': folder.pk})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Folder.objects.filter(user=godzilla).count(), 0)
        godzilla.delete()

    def test_delete_unknown_folder(self):
        """Try to delete a folder that does not exists, should
        raise a 404"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.post('/folder/delete/', {'object_id': 1})
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_delete_not_owned_folder(self):
        """Try to delete a folder owned by someone else""" 
        godzilla = self.user('godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        leviathan = self.user('leviathan')
        self.client.login(username='leviathan', password='leviathan')
        response = self.client.post('/folder/delete/', {'object_id': folder.pk})
        self.assertEquals(response.status_code, 403)
        godzilla.delete()
        leviathan.delete()


class FolderDeleteConfirmationObjectTests(BaseFavoritesTestCase):
    def test_confirmation(self):
        """Test that the page is reachable with an existing folder"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        response = self.client.get('/folder/delete/%s' % folder.pk)
        self.assertEquals(response.status_code, 200)
        folder.delete()
        godzilla.delete()

    def test_confirmation_unknown_folder(self):
        """If you try to delete an unknow folder, the server
        answer 404"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/folder/delete/%s' % 1)
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_confirmation_credentials(self):
        """Tests that the user is redirect if not logged in"""
        godzilla = self.user('godzilla')
        response = self.client.get('/folder/delete/%s' % 1)
        self.assertEquals(response.status_code, 302)
        godzilla.delete()


class FolderUpdateTests(BaseFavoritesTestCase):
    def test_show_page(self):
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        response = self.client.get('/folder/update/%s' % folder.pk)
        self.assertEquals(response.status_code, 200)
        godzilla.delete()
        folder.delete()

    def test_credentials(self):
        godzilla = self.user('godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        response = self.client.get('/folder/update/%s' % folder.pk)
        self.assertEquals(response.status_code, 302)
        folder.delete()
        godzilla.delete()


    def test_is_not_owner(self):
        """if the an user try to delete a favorite that
        he does not own, the server should answer a 403"""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=leviathan)
        folder.save()
        response = self.client.get('/folder/update/%s' % folder.pk)
        self.assertEquals(response.status_code, 403)
        godzilla.delete()
        leviathan.delete()
        folder.delete()

    def test_folder_does_not_exists(self):
        """If the user try to delete a folder that does not
        exists, the server returns a 404"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/folder/update/%s' % 1)
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_submit(self):
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        response = self.client.post('/folder/update/%s' % folder.pk,
                                    {'name': 'Nippon-koku'})
        self.assertEquals(response.status_code, 302)
        folder = Folder.objects.get(pk=folder.pk)
        self.assertEquals(folder.name, 'Nippon-koku')
        godzilla.delete()
        folder.delete()


class FavoriteListTests(BaseFavoritesTestCase):
    def test_favorite_list(self):
        """A user get access to its favorites"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        Favorite.objects.create_favorite(dummy, godzilla)
        response = self.client.get('/favorites/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['object_list']), 1)
        dummy.delete()
        godzilla.delete()

    def test_favorite_list(self):
        """Don't list objects that are not owned by the user"""
        leviathan = self.user('leviathan')
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        Favorite.objects.create_favorite(dummy, leviathan)
        response = self.client.get('/favorites/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['object_list']), 0)
        dummy.delete()
        godzilla.delete()
        leviathan.delete()

    def test_credentials(self): 
        """user should be logged in"""
        response = self.client.get('/favorites/')
        self.assertEquals(response.status_code, 302)


class FavoriteAddConfirmationTests(BaseFavoritesTestCase):
    def test_show_page(self):
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        response = self.client.get('/favorite/add/favorites/dummymodel/%s'
                                   % dummy.pk)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'].pk, dummy.pk)
        dummy.delete()
        godzilla.delete()

    def test_invalid_model(self):
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/favorite/add/foo/bar/1')
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_object_does_not_exists(self):
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/favorite/add/favorites/dummy/1')
        self.assertEquals(response.status_code, 404)
        godzilla.delete()


    def test_login_required(self):
        response = self.client.get('/favorite/add/favorites/dummy/1')
        self.assertEquals(response.status_code, 302)


class AddFavoriteTests(BaseFavoritesTestCase):
    def test_login_required(self):
        response = self.client.get('/favorite/add/')
        self.assertEquals(response.status_code, 302)

    def test_no_get(self):
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get('/favorite/add/')
        self.assertEquals(response.status_code, 400)
        godzilla.delete()

    def test_submit(self):
        pass

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
