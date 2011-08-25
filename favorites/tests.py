from django.db import models
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from django.db import models
from django.core.urlresolvers import reverse

from models import Favorite
from models import Folder
from managers import FavoritesManagerMixin


class DummyModel(models.Model):
    pass


class BarModel(models.Model):
    pass


class BaseFavoritesTestCase(TestCase):
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
    """Tests for ``folder_list`` url."""

    def test_get(self):
        """Test that ``folder_list`` url.

        Tests that the ``folder_list`` url returns a template
        in which user's folders were in the context."""
        godzilla = self.user('godzilla')

        Folder(name="foo", user=godzilla).save()
        Folder(name="bar", user=godzilla).save()

        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get(reverse('favorites:folder_list'))

        for folder in response.context['object_list']:
            self.assertIn(folder.name, ['foo', 'bar'])
        godzilla.delete()

    def test_get_empty(self):
        """Tests that ``folder_list`` url list nothing.

        Tests that the ``folder_list`` url returns a templates
        in which user's folders are injects, except that the user
        has no folders. this test testify that an user only his or her
        folders."""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')

        Folder(name="foo", user=godzilla).save()
        Folder(name="bar", user=godzilla).save()

        self.client.login(username='leviathan', password='leviathan')
        response = self.client.get(reverse('favorites:folder_list'))
        self.assertEquals(len(response.context['object_list']), 0)

        Folder.objects.all().delete()
        godzilla.delete()

    def test_login_required(self):
        """Test that ``folder_list`` url requires that the user is logged in.

        If the user is not logged the should be redirected to login page."""
        response = self.client.get(reverse('favorites:folder_list'))
        self.assertEquals(response.status_code, 302)


class FolderAddTests(BaseFavoritesTestCase):
    """Tests for ``folder_add`` url."""

    def test_get(self):
        """A logged in user try to fetch the formular. Returns a 200."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get(reverse('favorites:folder_add'))
        self.assertEquals(response.status_code, 200)
        godzilla.delete()

    def test_login_required(self):
        """Not logged user haven't access to this page. Redirects to login page."""
        response = self.client.get(reverse('favorites:folder_add'))
        self.assertEquals(response.status_code, 302)

    def test_post(self):
        """A logged in user try to add a new folder. Returns a redirect.

        A logged in user submit a valid form, the folder is added and the user
        is redirected"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.post(reverse('favorites:folder_add'), {'name': 'japan'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Folder.objects.filter(user=godzilla).count(), 1)
        Folder.objects.all().delete()
        godzilla.delete()


class FolderDeleteTests(BaseFavoritesTestCase):
    """Tests for ``folder_delete`` url."""

    def test_login_required(self):
        """The user should be logged in to delete something."""
        response = self.client.get(reverse('favorites:folder_delete', args=(1,)))
        self.assertEquals(response.status_code, 302)

    def test_post(self):
        """Submit a delete form with good credentials. Returns a redirect."""
        godzilla = self.user('godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.post(reverse('favorites:folder_delete', args=(folder.pk,)), {'object_id': folder.pk})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Folder.objects.filter(user=godzilla).count(), 0)
        godzilla.delete()

    def test_unknown_folder(self):
        """Try to delete a folder that does not exists. Returns a 404."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.post(reverse('favorites:folder_delete', args=(0,)), {'object_id': 1})
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_invalid_permission(self):
        """Try to delete a folder owned by someone else. Returns a 403."""
        godzilla = self.user('godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        leviathan = self.user('leviathan')
        self.client.login(username='leviathan', password='leviathan')
        response = self.client.post(reverse('favorites:folder_delete', args=(folder.pk,)), {'object_id': folder.pk})
        self.assertEquals(response.status_code, 403)
        godzilla.delete()
        leviathan.delete()

    def test_get(self):
        """Test that the page is reachable with an existing folder."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        response = self.client.get(reverse('favorites:folder_delete', args=(folder.pk,)))
        self.assertEquals(response.status_code, 200)
        folder.delete()
        godzilla.delete()

    def test_unknown_folder(self):
        """If you try to delete an unknow folder. Returns 404."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get(reverse('favorites:folder_delete', args=(0,)))
        self.assertEquals(response.status_code, 404)
        godzilla.delete()


class FolderUpdateTests(BaseFavoritesTestCase):
    """Tests for ``folder_update`` url."""

    def test_get(self):
        """User want to update an existing folder."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        response = self.client.get(reverse('favorites:folder_update', args=(folder.pk,)))
        self.assertEquals(response.status_code, 200)
        godzilla.delete()
        folder.delete()

    def test_login_required(self):
        """User should be logged it to delete an object."""
        godzilla = self.user('godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        response = self.client.get(reverse('favorites:folder_update', args=(folder.pk,)))
        self.assertEquals(response.status_code, 302)
        folder.delete()
        godzilla.delete()


    def test_invalid_permission_on_favorite(self):
        """User should own the folder to delete it. Returns a 403."""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=leviathan)
        folder.save()
        response = self.client.get(reverse('favorites:folder_update', args=(folder.pk,)))
        self.assertEquals(response.status_code, 403)
        godzilla.delete()
        leviathan.delete()
        folder.delete()

    def test_unknown_folder(self):
        """User try to delete a folder that does not exists. Returns a 404."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        response = self.client.get(reverse('favorites:folder_update', args=(0,)))
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_post(self):
        """User submit a valid POST request, updating the folder. Returns a redirect."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        response = self.client.post(reverse('favorites:folder_update', args=(folder.pk,)),
                                    {'name': 'Nippon-koku'})
        self.assertEquals(response.status_code, 302)
        folder = Folder.objects.get(pk=folder.pk)
        self.assertEquals(folder.name, 'Nippon-koku')
        godzilla.delete()
        folder.delete()


class FavoriteListTests(BaseFavoritesTestCase):
    """Tests for ``favorite_list`` url."""

    def test_get(self):
        """User list his or her favorites."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        Favorite.objects.create_favorite(dummy, godzilla)
        response = self.client.get(reverse('favorites:favorite_list'))
        self.assertEquals(response.status_code, 200)
        dummy.delete()
        godzilla.delete()

    def test_get_owned_favorites_only(self):
        """User only has access to his or her favorites."""
        leviathan = self.user('leviathan')
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        Favorite.objects.create_favorite(dummy, leviathan)
        response = self.client.get(reverse('favorites:favorite_list'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['favorites']), 0)
        dummy.delete()
        godzilla.delete()
        leviathan.delete()

    def test_login_required(self):
        """User should be logged in."""
        response = self.client.get(reverse('favorites:favorite_list'))
        self.assertEquals(response.status_code, 302)


class AddFavoriteTests(BaseFavoritesTestCase):
    """Tests for ``favorite_add`` url."""

    def test_get(self):
        """User access the form to add a favorite for an object."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        target_url = reverse('favorites:favorite_add', kwargs={
    'app_label': DummyModel._meta.app_label,
    'object_name': dummy._meta.module_name,
    'object_id': dummy.pk
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'].pk, dummy.pk)
        dummy.delete()
        godzilla.delete()

    def test_invalid_model(self):
        """User try to favorite an invalid model object. Returns a 400."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_add', kwargs={
    'app_label': 'foo',
    'object_name': 'bar',
    'object_id': '0'
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 400)
        godzilla.delete()

    def test_unknown_object(self):
        """User try to favorite an unknown object. Returns a 400."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_add', kwargs={
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name,
    'object_id': 3
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 400)
        godzilla.delete()

    def test_login_required(self):
        """User should be logged in"""
        target_url = reverse('favorites:favorite_add', kwargs={  # The target model
    'app_label': DummyModel._meta.app_label,            # doesn't have to be valid
    'object_name': DummyModel._meta.module_name,
    'object_id': 1
})
        response = self.client.get(target_url)
        login_url = reverse('django.contrib.auth.views.login')
        redirect_url_test = '%s?next=%s' % (login_url, target_url)
        self.assertRedirects(response, redirect_url_test)

    def test_post(self):
        """User submit a valid form, the favorite is added to his or her favorites."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=godzilla)
        folder.save()
        dummy = DummyModel()
        dummy.save()
        target_url = reverse('favorites:favorite_add', kwargs={  # The target model
    'app_label': DummyModel._meta.app_label,            # doesn't have to be valid
    'object_name': DummyModel._meta.module_name,
    'object_id': dummy.pk
})
        response = self.client.post(target_url,
                                    {'folder_id': folder.pk})
        self.assertEquals(response.status_code, 302)
        godzilla.delete()
        folder.delete()
        dummy.delete()

    def test_invalid_permission_on_folder(self):
        """User submits a form with a folder that is not his or her, renders the form."""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        folder = Folder(name='japan', user=leviathan)
        folder.save()
        dummy = DummyModel()
        dummy.save()
        target_url = reverse('favorites:favorite_add', kwargs={
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name,
    'object_id': dummy.pk
})
        response = self.client.post(target_url,
                                    {'folder_id': folder.pk})
        # form validation makes it impossible for a rogue user
        # to a favorite that i do not own
        self.assertEqual(response.status_code, 200)
        godzilla.delete()
        folder.delete()
        dummy.delete()
        leviathan.delete()

    def test_unknown_model(self):
        """User submits try to favorite an object with an unknown model. Returns a 400."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_add', kwargs={
    'app_label': 'foo',
    'object_name': 'bar',
    'object_id': 0
})
        response = self.client.post(target_url)
        self.assertEquals(response.status_code, 400)
        godzilla.delete()


class DeleteFavoriteTests(BaseFavoritesTestCase):
    """Tests for ``favorite_delete`` url"""

    def test_login_required(self):
        """The user should be logged in to be able to delete a favorite."""
        target = reverse('favorites:favorite_delete', kwargs={'object_id': 123})
        response = self.client.post(target)
        self.assertEquals(response.status_code, 302)

    def test_post(self):
        """User submits a valid form the favorite is deleted and the user redirected."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        target_url = reverse('favorites:favorite_delete', kwargs={'object_id': favorite.pk})
        response = self.client.post(target_url,
                                    {'object_id': favorite.pk})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(Favorite.objects.all()), 0)
        favorite.delete()
        godzilla.delete()

    def test_invalid_object(self):
        """Submit a form with an unknown object, should raise a 404."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        # Both the get "parameter"
        target_url = reverse('favorites:favorite_delete', kwargs={'object_id': favorite.pk})
        # and POST parameter are invalid
        post_values = {'object_id': 0}
        response = self.client.post(target_url, post_values)
        self.assertEquals(response.status_code, 404)
        godzilla.delete()


    def test_invalid_permission(self):
        """User try to delete a favorite owned by someone else. Returns a 403."""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, leviathan)
        target_url = reverse('favorites:favorite_delete', kwargs={'object_id': favorite.pk})
        response = self.client.post(target_url,
                                    {'object_id': favorite.pk})
        self.assertEquals(response.status_code, 403)
        favorite.delete()
        godzilla.delete()


class DeleteFavoriteForObjectTests(BaseFavoritesTestCase):
    """Tests for ``favorite_delete_by_object`` url."""

    def test_login_required(self):
        """User should be logged in."""
        target_url = reverse('favorites:favorite_delete_for_object',
                         kwargs={ # whatever the object even an invalid objects
    'app_label': 'foo',
    'object_name': 'bar',
    'object_id': 0
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 302)

    def test_invalid_model(self):
        """User try to delete an object with an unknown model. Returns a 400."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_delete_for_object',
                         kwargs={
    'app_label': 'foo',
    'object_name': 'bar',
    'object_id': 0
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 400)
        godzilla.delete()

    def test_unknown_object(self):
        """User try to delete an unknown object. Returns a 400."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_delete_for_object',
                         kwargs={
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name,
    'object_id': 0
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 400)
        godzilla.delete()

    def test_unknown_favorite(self):
        """User try to delete an unknown favorite. Returns 404."""
        godzilla = self.user('godzilla')
        dummy = DummyModel()
        dummy.save()
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_delete_for_object',
                         kwargs={
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name,
    'object_id': dummy.pk
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_get(self):
        """User submits a valid form, the favorite is deleted, and user redirected."""
        godzilla = self.user('godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_delete_for_object',
                         kwargs={
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name,
    'object_id': dummy.pk
})
        response = self.client.get(target_url)
        redirect_url = reverse('favorites:favorite_delete', kwargs={'object_id': favorite.pk})
        self.assertRedirects(response, redirect_url)
        godzilla.delete()
        dummy.delete()
        favorite.delete()


class DeleteFavoriteTests(BaseFavoritesTestCase):  # FIXME: remove because doublon
    """Tests for ``delete url."""

    def test_login_required(self):
        """User should be logged in."""
        # whatever the favorite even invalid
        target_url = reverse('favorites:favorite_delete', kwargs={'object_id': 0})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 302)

    def test_unknown_favorite(self):
        """Should return 404 if there is no such favorite."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_delete', kwargs={'object_id': 123})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_get(self):
        """Should return a page that show up a form to validate deletion"""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        target_url = reverse('favorites:favorite_delete', kwargs={'object_id': favorite.pk})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])
        self.assertIsNotNone(response.context['favorite'])
        self.assertEquals(response.context['favorite'].pk, favorite.pk)
        self.assertEquals(response.context['favorite'].content_object.pk, dummy.pk)
        godzilla.delete()
        dummy.delete()
        favorite.delete()


class FavoriteContentTypeList(BaseFavoritesTestCase):
    """Tests for ``favorite_content_type_list`` url."""

    def test_login_required(self):
        """User should be logged in."""
        target_url = reverse('favorites:favorite_content_type_list',
                             kwargs = {
    'app_label': 'foo',
    'object_name': 'bar'
})
        response = self.client.get('/favorite/bar/foo/')
        self.assertEquals(response.status_code, 302)

    def test_get_owned_favorites_only(self):
        """User should only see her/his favorites."""
        # setup
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        def create_object_n_favorite(user, folder=None):
            dummy = DummyModel()
            dummy.save()
            favorite = Favorite.objects.create_favorite(dummy, user, folder)
            return dummy, favorite
        godzilla_instances =  []
        godzilla_favorite_pks = []
        for i in range(5):
            instance, favorite = create_object_n_favorite(godzilla)
            godzilla_instances.append((instance, favorite))
            godzilla_favorite_pks.append(favorite.pk)
        japan = Folder(name='japan', user=godzilla)
        japan.save()
        for i in range(5):
            instance, favorite = create_object_n_favorite(godzilla, japan)
            godzilla_instances.append((instance, favorite))
            godzilla_favorite_pks.append(favorite.pk)
        leviathan_instances = []
        for i in range(5):
            leviathan_instances.append(create_object_n_favorite(leviathan))

        # tests
        target_url = reverse('favorites:favorite_content_type_list',
                             kwargs = {
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(response.context['favorites'])
        for instance in response.context['favorites']:
            self.assertIn(instance.pk, godzilla_favorite_pks)

        # teardown
        for instances in (leviathan_instances, godzilla_instances):
            for instance, favorite in instances:
                instance.delete()
                favorite.delete()
        godzilla.delete()
        leviathan.delete()

    def test_content_type_favorites_only(self):
        """User should only see favorite for the requetes content type."""
        # setup
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        def create_object_n_favorite(model, user):
            dummy = model()
            dummy.save()
            favorite = Favorite.objects.create_favorite(dummy, user)
            return dummy, favorite
        godzilla_instances =  []
        godzilla_dummymodel_favorite_pks = []
        for i in range(5):
            instance, favorite = create_object_n_favorite(DummyModel, godzilla)
            godzilla_dummymodel_favorite_pks.append(favorite.pk)
            godzilla_instances.append((instance, favorite))

        for i in range(5):
            instance, favorite = create_object_n_favorite(BarModel, godzilla)
            godzilla_instances.append((instance, favorite))

        # tests
        target_url = reverse('favorites:favorite_content_type_list',
                             kwargs = {
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(response.context['favorites'])
        for instance in response.context['favorites']:
            self.assertIn(instance.pk, godzilla_dummymodel_favorite_pks)

        # teardown
        for instance, favorite in godzilla_instances:
            instance.delete()
            favorite.delete()
        godzilla.delete()


    def test_unknown_model(self):
        """User try to see favorites for an unknown model. Returns a 400."""
        # setup
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')

        # tests
        target_url = reverse('favorites:favorite_content_type_list',
                             kwargs = {
    'app_label': 'foo',
    'object_name': 'bar'
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 400)

        godzilla.delete()


class MoveFavoriteTests(BaseFavoritesTestCase):
    """Tests for ``favorite_move`` url."""

    def test_login_required_get(self):
        """User should be logged in."""
        target_url = reverse('favorites:favorite_move',
                             kwargs = {
    'object_id': 0,
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 302)

    def test_login_required_post(self):
        """User should be logged to post."""
        target_url = reverse('favorites:favorite_move',
                             kwargs = {
    'object_id': 0,
})
        response = self.client.post(target_url)
        self.assertEquals(response.status_code, 302)

    def test_get(self):
        """A logged in user ask to move a valid favorite."""
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
        target_url = reverse('favorites:favorite_move',
                             kwargs = {
    'object_id': favorite.pk,
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 200)

        instance = response.context['favorite']
        self.assertEquals(instance.pk, favorite.pk)
        favorite.delete()
        godzilla.delete()
        for folder in folders:
            folder.delete()
        dummy.delete()

    def test_unknown_object(self):
        """User try to move an unknown favorite. Returns a 404."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_move',
                             kwargs = {
    'object_id': 0,
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_invalid_permission_favorite(self):
        """User try to move an object owned by someone else. Returns a 404."""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, leviathan)
        target_url = reverse('favorites:favorite_move',
                             kwargs = {
    'object_id': favorite.pk,
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 403)
        favorite.delete()
        godzilla.delete()
        leviathan.delete()
        dummy.delete()

    def test_post(self):
        """User submits a valid form, favorites moved, and user redirected."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        folder = Folder(name="japan", user=godzilla)
        folder.save()
        target_url = reverse('favorites:favorite_move',
                             kwargs = {
    'object_id': favorite.pk,
})
        post_values = {'object_id': favorite.pk, 'folder_id': folder.pk}
        response = self.client.post(target_url, post_values)
        self.assertEquals(response.status_code, 302)
        instance = Favorite.objects.get(pk=favorite.pk)
        self.assertEqual(folder.pk, instance.folder.pk)
        folder.delete()
        favorite.delete()
        godzilla.delete()
        dummy.delete()

    def test_post_invalid_permission_on_folder(self):
        """User try to move a favorite to of folder he or she doesn't own. Returns the form."""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        folder = Folder(name="china", user=leviathan)
        folder.save()
        target_url = reverse('favorites:favorite_move',
                             kwargs = {
    'object_id': favorite.pk,
})
        post_values = {'object_id': favorite.pk, 'folder_id': folder.pk}
        response = self.client.post(target_url, post_values)
        self.assertEquals(response.status_code, 200)
        folder.delete()
        favorite.delete()
        godzilla.delete()
        leviathan.delete()
        dummy.delete()

    def test_post_unknown_folder(self):
        """User try to move a favorite to an unknown folder. Returns the form."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        target_url = reverse('favorites:favorite_move',
                             kwargs = {
    'object_id': favorite.pk,
})
        post_values = {'object_id': favorite.pk, 'folder_id': 1}
        response = self.client.post(target_url, post_values)
        self.assertEquals(response.status_code, 200)
        favorite.delete()
        godzilla.delete()
        dummy.delete()

    def test_post_move_to_root(self):
        """User moves a favorite to root folder (no folder). Moves the favorite,
        and redirect the user."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(dummy, godzilla)
        target_url = reverse('favorites:favorite_move',
                             kwargs = {
    'object_id': favorite.pk,
})
        post_values = {'object_id': favorite.pk, 'folder_id': ''}
        response = self.client.post(target_url, post_values)
        self.assertEquals(response.status_code, 302)
        instance = Favorite.objects.get(pk=favorite.pk)
        self.assertIsNone(instance.folder)
        favorite.delete()
        godzilla.delete()
        dummy.delete()


class ContentTypeByFolderListTests(BaseFavoritesTestCase):
    """Tests url ``favorite_content_type_and_folder_list`` url."""

    def test_login_required(self):
        """User should be logged in"""
        target_url = reverse('favorites:favorite_content_type_and_folder_list',
                             kwargs = {
    'app_label': 'foo',
    'object_name': 'bar',
    'folder_id': 0
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 302)

    def test_invalid_model(self):
        """User try to list favorites for a model that does not exists. Returns a 400."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_content_type_and_folder_list',
                             kwargs = {
    'app_label': 'foo',
    'object_name': 'bar',
    'folder_id': 0
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 400)
        godzilla.delete()

    def test_unknown_folder(self):
        """User try to list favorites for a folder that does not exists. Returns a 404."""
        godzilla = self.user('godzilla')
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_content_type_and_folder_list',
                             kwargs = {
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name,
    'folder_id': 0
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 404)
        godzilla.delete()

    def test_invalid_permission_on_folder(self):
        """User try to list favorites for a folder he or she doesn't own. Returns a 403."""
        godzilla = self.user('godzilla')
        leviathan = self.user('leviathan')
        folder = Folder(name='china', user=leviathan)
        folder.save()
        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_content_type_and_folder_list',
                             kwargs = {
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name,
    'folder_id': folder.pk
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 403)
        godzilla.delete()
        leviathan.delete()
        folder.delete()

    def test_get(self):
        """User request a valid content type / folder combination. Returns 200."""
        godzilla = self.user('godzilla')
        japan = Folder(name='japan', user=godzilla)
        japan.save()
        china = Folder(name='china', user=godzilla)
        china.save()

        def create_favorites(model, folder):
            m = model()
            m.save()
            favorite = Favorite.objects.create_favorite(m, godzilla, folder)
            return m, favorite

        japan_folder_pks = []
        instances = []
        for _ in range(5):
            instance, favorite = create_favorites(DummyModel, japan)
            japan_folder_pks.append(favorite.pk)
            instances.append((instance, favorite))

        for _ in range(5):
            instance, favorite = create_favorites(DummyModel, china)
            instances.append((instance, favorite))

        for _ in range(5):
            instance, favorite = create_favorites(BarModel, japan)
            instances.append((instance, favorite))

        for _ in range(5):
            instance, favorite = create_favorites(BarModel, china)
            instances.append((instance, favorite))

        self.client.login(username='godzilla', password='godzilla')
        target_url = reverse('favorites:favorite_content_type_and_folder_list',
                             kwargs = {
    'app_label': DummyModel._meta.app_label,
    'object_name': DummyModel._meta.module_name,
    'folder_id': japan.pk
})
        response = self.client.get(target_url)
        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(response.context['favorites'])
        for instance in response.context['favorites']:
            self.assertIn(instance.pk, japan_folder_pks)

        godzilla.delete()
        for instance in instances:
            instance[0].delete()
            instance[1].delete()
        japan.delete()
        china.delete()


class MoveFavoriteConfirmation(TestCase):
    """Tests for ``favorite_move`` url``"""

    def test_login_required(self):
        """User should be logged in"""
        client = Client()
        target_url = reverse('favorites:favorite_move_to_folder',
                             kwargs={'favorite_id': 1, 'folder_id': 2})
        response = client.get(target_url,
                              follow=True)
        redirect_url, status = response.redirect_chain[0]
        self.assertEqual(status, 302)
        test_redirect = 'http://testserver/accounts/login/?next=%s' % target_url
        self.assertEqual(redirect_url, test_redirect)


    def test_invalid_permission_on_folder(self):
        """User try to move a favorite to a folder he doesn't own. Returns a 403."""
        user = User.objects.create(username='user')
        user.set_password('user')
        user.save()
        user2 = User.objects.create(username='user2')
        user2.set_password('user2')
        user2.save()
        folder = Folder(user=user2, name='name')
        folder.save()
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(user=user,
                                                    content_object=dummy)
        target_url = reverse('favorites:favorite_move_to_folder',
                             kwargs={'favorite_id': favorite.pk, 'folder_id': folder.pk})
        client = Client()
        self.assertTrue(client.login(username='user', password='user'))
        response = client.get(target_url)
        self.assertEqual(response.status_code, 403)

    def test_invalid_permission_on_favorite(self):
        """User try to move a favorite he or she doesn't own. Returns a 403."""
        user = User.objects.create(username='user')
        user.set_password('user')
        user.save()
        user2 = User.objects.create(username='user2')
        user2.set_password('user2')
        user2.save()
        folder = Folder(user=user, name='name')
        folder.save()
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(user=user2,
                                                    content_object=dummy)
        target_url = reverse('favorites:favorite_move_to_folder',
                             args=(favorite.pk,
                                   folder.pk))
        client = Client()
        self.assertTrue(client.login(username='user', password='user'))
        response = client.get(target_url)
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        """User make a valid request, returns a 200"""
        user = User.objects.create(username='user')
        user.set_password('user')
        user.save()
        folder = Folder(user=user, name='name')
        folder.save()
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(user=user,
                                                    content_object=dummy)
        target_url = reverse('favorites:favorite_move_to_folder',
                             args=(favorite.pk,
                                   folder.pk))
        client = Client()
        self.assertTrue(client.login(username='user', password='user'))
        response = client.get(target_url)
        self.assertEqual(response.status_code, 200)

class ToggleShareFavoritesTests(TestCase):
    """Test ``favorite_share_toggle`` url."""

    def test_login_required(self):
        """User should be logged in."""
        target_url = reverse('favorites:favorite_toggle_share',
                             kwargs={'favorite_id': 0})
        client = Client()
        response = client.get(target_url, follow=True)
        redirect_url, status = response.redirect_chain[0]
        self.assertEqual(status, 302)
        login_test_url = 'http://testserver/accounts/login/?next=%s' % target_url
        self.assertEqual(redirect_url, login_test_url)

    def test_get(self):
        """User make a valid request. Returns a 200."""
        user = User.objects.create(username='user')
        user.set_password('user')
        user.save()
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(user=user,
                                                    content_object=dummy)
        favorite.save()

        target_url = reverse('favorites:favorite_toggle_share',
                             kwargs={'favorite_id': favorite.pk,})

        client = Client()
        self.assertTrue(client.login(username='user', password='user'))
        response = client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['favorite'].pk, favorite.pk)

    def test_invalid_permission(self):
        """User try to toggle share on a favorite he does not own. Returns a 403."""
        user = User.objects.create(username='user')
        user.set_password('user')
        user.save()
        user2 = User.objects.create(username='user2')
        user2.set_password('user2')
        user2.save()
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(user=user2,
                                                    content_object=dummy)
        favorite.save()
        target_url = reverse('favorites:favorite_toggle_share',
                             kwargs={'favorite_id': favorite.pk,})
        client = Client()
        self.assertTrue(client.login(username='user', password='user'))
        response = client.get(target_url)
        self.assertEqual(response.status_code, 403)

    def test_post(self):
        """User submits a valid form, the folder change share states, user is redirected."""
        user = User.objects.create(username='user', email="user@example.org")
        user.set_password('user')
        user.save()
        dummy = DummyModel()
        dummy.save()
        favorite = Favorite.objects.create_favorite(user=user,
                                                    content_object=dummy)
        favorite.save()

        target_url = reverse('favorites:favorite_toggle_share',
                             kwargs={'favorite_id': favorite.pk,})


        self.assertTrue(self.client.login(username='user', password='user'))
        response = self.client.post(target_url)
        self.assertEqual(response.status_code, 302) # FIXME test redirect
        favorite = Favorite.objects.get(pk=favorite.pk)
        self.assertTrue(favorite.shared)

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
