import urlparse

from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.db.models import get_model
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.utils import simplejson

from django.core.urlresolvers import reverse

from favorites.models import Favorite
from favorites.models import Folder

from favorites.forms import ObjectIdForm, ObjectHiddenForm
from favorites.forms import FolderForm
from favorites.forms import CreateFavoriteForm
from favorites.forms import UpdateFavoriteForm
from favorites.forms import FavoriteMoveHiddenForm
from favorites.forms import ValidationForm

def _validate_next_parameter(request, next):
    parsed = urlparse.urlparse(next)
    if parsed and parsed.path:
        return parsed.path
    return None

# Taken from https://github.com/ericflo/django-avatar/blob/master/avatar/views.py
def _get_next(request):
    """
    The part that's the least straightforward about views in this module is how they
    determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, the view will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the view will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the view will
    redirect to that previous page.
    """
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    if next:
        next = _validate_next_parameter(request, next)
    if not next:
        next = request.path
    return next


### FOLDER VIEWS ###########################################################

@login_required
def list_folder(request):
    object_list = Folder.objects.filter(user=request.user)
    ctx = RequestContext(request, {'object_list': object_list})
    return render_to_response('favorites/folder_list.html', ctx)


@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            Folder(name=name, user=request.user).save()
            return redirect(_get_next(request))
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
            return redirect(_get_next(request))
    form = FolderForm(initial={'name': folder.name})
    next = request.GET.get('next', None)
    return render_to_response('favorites/folder_update.html',
                               RequestContext(request, {'form': form,
                                                        'next': next,
                                                        'folder': folder}))


@login_required
def delete_folder(request, object_id):
    folder = get_object_or_404(Folder, pk=object_id)
    if request.user != folder.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        folder.delete()
        return redirect(_get_next(request))
    folder = get_object_or_404(Folder, pk=object_id)
    next = request.GET.get('next', None)
    return render_to_response('favorites/folder_delete.html',
                              RequestContext(request, {'folder': folder,
                                                       'next': next}))

### FAVORITE VIEWS #########################################################


@login_required
def list_favorites(request):
    object_list = Favorite.objects.favorites_for_user(request.user)
    ctx = {'favorites': object_list}
    ctx = RequestContext(request, ctx)
    return render_to_response('favorites/favorite_list.html', ctx)


@login_required
def create_favorite(request,
                    app_label,
                    object_name,
                    object_id):
    """Renders a formular to get confirmation to favorite the
    object represented by `app_label`, `object_name` and `object_id`
    creation. It raise a 404 exception if there is not such object.
    If it's a POST creates the favorite object if there isn't
    any such favorite already. If validation fails the it returns the
    with an insightful error. If the validation succeed the favorite is
    added to user profile and a redirection is returned"""
    choices = [(0, '')]
    query = Folder.objects.filter(user=request.user)
    folder_choices = query.order_by('name').values_list('pk', 'name')
    choices.extend(folder_choices)

    if request.method == 'POST':
        form = CreateFavoriteForm(choices=choices, data=request.POST)

        if form.is_valid():
            app_label = form.cleaned_data['app_label']
            object_name = form.cleaned_data['object_name']
            object_id = form.cleaned_data['object_id']

            folder_id = form.cleaned_data['folder']

            if folder_id == '0':
                folder = None
            else:
                folder = get_object_or_404(Folder, pk=folder_id)
                if request.user != folder.user:
                    return HttpResponseForbidden()

            model = get_model(app_label, object_name)
            try:
                content_type = ContentType.objects.get_for_model(model)
            except AttributeError: # there no such model
                return HttpResponseNotFound()
            obj = content_type.get_object_for_this_type(pk=object_id)

            if not Favorite.objects.filter(content_type=content_type,
                                           object_id=object_id,
                                           user=request.user):
                Favorite.objects.create_favorite(obj,
                                                 request.user,
                                                 folder)
            return redirect(_get_next(request))
    else:
        initial = {'app_label': app_label,
                   'object_name': object_name,
                   'object_id': object_id}
        if len(choices) == 1:
            form = ObjectHiddenForm(initial=initial)
        else:
            form = CreateFavoriteForm(choices=choices, initial=initial)

    model = get_model(app_label, object_name)
    if model is None:
        return HttpResponseBadRequest()
    object = get_object_or_404(model, pk=object_id)

    ctx = {'form': form, 'object': object, 'next':_get_next(request)}
    ctx = RequestContext(request, ctx)
    return render_to_response('favorites/favorite_add.html', ctx)


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
def delete_favorite_for_object(request,
                               app_label,
                               object_name,
                               object_id):
    """Renders a formular to get confirmation to unfavorite the
    object represented by `app_label`, `object_name` and `object_id`.
    It raise a 404 exception if there is not such object."""
    model = get_model(app_label, object_name)
    try:
        object = get_object_or_404(model, pk=object_id)
    except AttributeError: # the model does not exists
        return HttpResponseNotFound()

    query = Favorite.objects.favorites_for_object(object, request.user)

    try:
        favorite = query[0]
    except:
        return HttpResponseNotFound()

    form = ObjectIdForm(initial={'object_id': favorite.pk})

    ctx = {'form': form, 'object': object, 'next': _get_next(request)}
    ctx = RequestContext(request, ctx)
    return render_to_response('favorites/favorite_delete.html', ctx)


@login_required
def delete_favorite(request, object_id):
    """Renders a formular to get confirmation to unfavorite the object
    the favorite that has ``object_id`` as id. It raise a 404 if there
    is not such a object, a HttpResponseForbidden if the favorite is not
    owned by current user"""
    favorite = get_object_or_404(Favorite, pk=object_id)
    if request.method == 'POST':
        form = ValidationForm(request.POST)
        if form.is_valid():
            if request.user == favorite.user:
                favorite.delete()
                return redirect(_get_next(request))
            else:
                return HttpResponseForbidden()
    instance = favorite.content_object
    form = ValidationForm()
    ctx = {'form': form, 'object': instance, 'next': _get_next(request)}
    ctx = RequestContext(request, ctx)
    return render_to_response('favorites/favorite_delete.html', ctx)

@login_required
def move_favorite(request, object_id):
    """Renders a formular to move a favorite to another folder"""
    favorite = get_object_or_404(Favorite, pk=object_id)
    if not favorite.user == request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        choices = [(0, '')]
        choices.extend(Folder.objects.filter(user=request.user).order_by('name').values_list('pk', 'name'))
        form = UpdateFavoriteForm(choices=choices, data=request.POST)

        if form.is_valid():
            folder_id = form.cleaned_data['folder']
            if folder_id == '0':
                folder = None
            else:
                folder = get_object_or_404(Folder, pk=folder_id)
            favorite.folder = folder
            favorite.save()
            return redirect(_get_next(request))

    dictionary = {
    'favorite': favorite,
    'next': _get_next(request),
    }
    return render(request,
                  'favorites/favorite_move.html',
                  dictionary)


@login_required
def move_favorite_confirmation(request, favorite_id, folder_id):
    """Confirm move before submitting action"""
    favorite = get_object_or_404(Favorite, pk=favorite_id)
    if request.user != favorite.user:
        return HttpResponseForbidden()
    folder = get_object_or_404(Folder, pk=folder_id)
    if request.user != folder.user:
        return HttpResponseForbidden()

    form = FavoriteMoveHiddenForm(initial={'folder': folder.pk,
                                           'object_id': favorite.pk})
    next = request.GET.get('next', None)

    ctx = {'form': form,
           'favorite': favorite,
           'folder': folder,
           'next': next}
    ctx = RequestContext(request, ctx)
    return render_to_response('favorites/favorite_move_confirmation.html', ctx)


@login_required
def toggle_share_favorite(request, favorite_id):
    """Confirm before submiting the toggle share action"""
    favorite = get_object_or_404(Favorite, pk=favorite_id)
    if request.user != favorite.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = ValidationForm(data=request.POST)
        if form.is_valid():
            favorite.shared = False if favorite.shared else True  # toggle
            favorite.save()
            return redirect(_get_next(request))
    else:
        form = ValidationForm()
    ctx = {'favorite': favorite}
    ctx = RequestContext(request, ctx)
    return render_to_response('favorites/favorite_toggle_share.html', ctx)


@login_required
def content_type_list(request, app_label, object_name, folder_id=None):
    """
    Retrieve favorites for a user by content_type.
    
    The optional folder_id parameter will be used to filter the favorites, if 
    passed.
    """
    model = get_model(app_label, object_name)
    if model is None:
        return HttpResponseBadRequest()
    content_type = ContentType.objects.get_for_model(model)
    
    filters = {"content_type":content_type, "user":request.user}
    templates = []
    context_data = {
        'app_label': app_label,
        'object_name': object_name,
        'folder': None
    }
    
    if folder_id:
        folder = get_object_or_404(Folder, pk=folder_id)
        if not folder.user == request.user:
            return HttpResponseForbidden()
        filters["folder"] = folder
        context_data["folder"] = folder
        dynamic_template = 'favorites/list_favorites_%s_%s_by_folder.html' \
                                                      % (app_label, object_name)
        templates.append(dynamic_template)
    
    favorites = Favorite.objects.filter(**filters)
    context_data["favorites"] = favorites
    
    # Set content_type specific and default templates
    dynamic_template = 'favorites/list_favorites_%s_%s.html' % (app_label,
                                                                    object_name)
    templates.append(dynamic_template)
    # Default
    templates.append('favorites/list_favorites_content_type.html')
    return render(request, templates, context_data)
