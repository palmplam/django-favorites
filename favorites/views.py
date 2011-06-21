from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.db.models import get_model
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.utils import simplejson
from django.core.urlresolvers import reverse

from favorites.models import Favorite
from favorites.models import Folder

from favorites.forms import DeleteFavoriteForm
from favorites.forms import CreateFavoriteHiddenForm

from favorites.forms import FolderForm
from favorites.forms import DeleteFolderForm


### FOLDER VIEWS ##############################################################


@login_required
def list_folder(request):
    object_list = Folder.objects.filter(user=request.user)
    return render_to_response('favorites/folder_list.html', 
                              RequestContext(request, {'object_list': object_list}))


@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            Folder(name=name, user=request.user).save()
            return redirect(request.GET.get('next', '/'))
    form = FolderForm()
    next = request.GET.get('next', None)
    return render_to_response('favorites/create_folder.html',
                              RequestContext(request, {'form': form,
                                                       'next': next}))


@login_required
def update_folder(request, object_id):
    folder = get_object_or_404(Folder, pk=object_id)

    if folder.user != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder.name = form.cleaned_data['name']
            folder.save()
            return redirect(request.GET.get('next', '/'))
    form = FolderForm(initial={'name': folder.name})
    next = request.GET.get('next', None)
    return render_to_response('favorites/folder_update.html',
                               RequestContext(request, {'form': form,
                                                        'next': next,
                                                        'folder': folder}))


@login_required
def delete_folder_confirmation(request, object_id):
    form = DeleteFolderForm(initial={'object_id': object_id})
    folder = get_object_or_404(Folder, pk=object_id)
    next = request.GET.get('next', None)
    return render_to_response('favorites/delete_folder_confirmation.html',
                              RequestContext(request, {'form': form,
                                                       'folder': folder,
                                                       'next': next}))
@login_required
def delete_folder(request):
    if request.method == 'POST':
        form = DeleteFolderForm(request.POST)
        if form.is_valid():
            object_id = form.cleaned_data['object_id']
            folder = get_object_or_404(Folder, pk=object_id)
            if request.user == folder.user:
                folder.delete()
                return redirect(request.GET.get('next', '/'))
            else:
                return HttpResponseForbidden()
    return HttpResponseBadRequest()


### FAVORITE VIEWS ############################################################


@login_required
def create_favorite_confirmation(request,
                                 app_label,
                                 object_name,
                                 object_id):
    """Renders a formular to get confirmation to favorite the
    object represented by `app_label`, `object_name` and `object_id`
    creation. It raise a 404 exception if there is not such object."""

    model = get_model(app_label, object_name)
    content_type = ContentType.objects.get_for_model(model)
    obj = content_type.get_object_for_this_type(pk=object_id)

    object = content_type.get_object_for_this_type(pk=object_id)

    initial = {'app_label': app_label,
               'object_name': object_name,
               'object_id': object_id}
    form = CreateFavoriteHiddenForm(initial=initial)

    ctx = {'form': form, 'object': obj, 'next':request.GET.get('next', '/')}
    ctx = RequestContext(request, ctx)
    return render_to_response('favorites/confirm_favorite.html', ctx)


@login_required
def create_favorite(request):
    """Validates POST and create the favorite object if there isn't
    any such favorite already. If validation fails the it returns a
    bad request error. If the validation succeed the favorite is added
    to user profile and a redirection is returned"""
    if request.method == 'POST':
        form  = CreateFavoriteHiddenForm(request.POST)
        if form.is_valid():
            app_label = form.cleaned_data['app_label']
            object_name = form.cleaned_data['object_name']
            object_id = form.cleaned_data['object_id']

            model = get_model(app_label, object_name)
            content_type = ContentType.objects.get_for_model(model)
            obj = content_type.get_object_for_this_type(pk=object_id)

            if not Favorite.objects.filter(content_type=content_type,
                                           object_id=object_id,
                                           user=request.user):
                Favorite.objects.create_favorite(obj, request.user)
            return redirect(request.GET.get('next', '/'))
    return HttpResponseBadRequest()


@login_required
def favorite_list_for_model_class(request, model_class, **kwargs):
    """
    Generic `favorites list` view based on generic object_list

    `model_class` - required valid model class

    Other parameters are same as object_list.

    Example of usage (urls.py):
        url(r'favorites/my_model/$',
            'favorites.views.favorite_list', kwargs={
                'model_class': get_model('my_app.MyModel'),
                'paginate_by': 25,
            }, name='favorites-mymodel')
    """
    default_queryset = Favorite.objects.favorites_for_model(model_class,
                                                            request.user)
    queryset = kwargs.get('queryset', default_queryset)
    return object_list(request, queryset, **kwargs)


@login_required
def delete_favorite(request, object_id, form_class=None, redirect_to=None,
           template_name=None, extra_context=None):
    """
    Generic Favorite object delete view

    GET: displays question to delete favorite
    POST: deletes favorite object and returns to `redirect_to`

    Default context:
        `form` - delete form

    `object_id` - required object_id (favorite pk)
    `template_name` - default "favorites/favorite_delete.html"
    `form_class` - default DeleteFavoriteForm
    `redirect_to` - default set to "favorites", change it if needed
    `extra_context` - provide extra context if needed
    """

    favorite = get_object_or_404(Favorite, pk=object_id, user=request.user)
    form_class = form_class or DeleteFavoriteForm

    if request.method == 'POST':
        form = form_class(instance=favorite, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(redirect_to or 'favorites')
    else:
        form = form_class(instance=favorite)
    ctx = extra_context or {}
    ctx.update({
        'form': form,
    })
    if template_name:
        return render_to_response(template_name,
                                  RequestContext(request, ctx))
    else:
        return render_to_response('favorites/favorite_delete.html',
                                  RequestContext(request, ctx))
