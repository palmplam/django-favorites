from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.db.models import get_model
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils import simplejson
from django.core.urlresolvers import reverse

from models import Favorite

from favorites.forms import DeleteFavoriteForm
from favorites.forms import CreateFavoriteHiddenForm


@login_required
def ajax_add_favorite(request):
    """ Adds favourite returns Http codes"""
    if request.method == "POST":
        object_id = request.POST.get("object_id")
        content_type = get_object_or_404(ContentType,
                                         pk=request.POST.get("content_type_id"))
        obj = content_type.get_object_for_this_type(pk=object_id)

        # check if it was created already
        if Favorite.objects.filter(content_type=content_type,
                                   object_id = object_id,
                                   user=request.user):
            # return conflict response code if already satisfied
            return HttpResponse(status=409)

        #if not create it
        favorite = Favorite.objects.create_favorite(obj, request.user)
        count = Favorite.objects.favorites_for_object(obj).count()
        return HttpResponse(simplejson.dumps({'count': count}),
                            'application/javascript',
                            status=200)
    else:
        return HttpResponse(status=405)


@login_required
def ajax_remove_favorite(request):
    """ Adds favourite returns Http codes"""
    if request.method == "POST":
        object_id = request.POST.get("object_id")
        content_type = get_object_or_404(ContentType,
                                         pk=request.POST.get("content_type_id"))
        favorite = get_object_or_404(Favorite, object_id=object_id,
                                               content_type=content_type,
                                               user=request.user)
        favorite.delete()
        obj = content_type.get_object_for_this_type(pk=object_id)
        count = Favorite.objects.favorites_for_object(obj).count()
        return HttpResponse(simplejson.dumps({'count': count}),
                            'application/javascript',
                            status=200)
    else:
        return HttpResponse(status=405)


@login_required
def create_favorite_confirmation(request,
                                 app_label,
                                 object_name,
                                 object_id):
    model = get_model(app_label, object_name)
    content_type = ContentType.objects.get_for_model(model)
    obj = content_type.get_object_for_this_type(pk=object_id)

    if Favorite.objects.filter(content_type=content_type,
                               object_id=object_id,
                               user=request.user):
        # FIXME: it's already a favorite what should we do ? (amirouche)
        pass

    initial = {'app_label': app_label,
               'object_name': object_name,
               'object_id': object_id}
    form = CreateFavoriteHiddenForm(initial=initial)

    ctx = RequestContext(request, {'form': form, 'object': obj})

    return render_to_response('favorites/confirm_favorite.html', ctx)


@login_required
def create_favorite(request, default_redirect='/'):
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
            try:
                return redirect(request.GET['next'])
            except:
                return redirect(default_redirect)

        else:
            args = (form.cleaned_data['app_label'],
                    form.cleaned_data['object_name'],
                    form.cleaned_data['object_id'])

            url = reverse('add-to-favorites-confirmation', args=args)
            return redirect(url)
    return HttpResponse(status=405)


@login_required
def favorite_list(request, model_class, **kwargs):
    """
    Generic `favorites list` view based on generic object_list

    `model_class` - required valid model class
    `template_name` - default is "favorites/favorite_list.html"
                      used by generic object_list view

    Other parameters are same as object_list.

    Example of usage (urls.py):
        url(r'favorites/my_model/$',
            'favorites.views.favorite_list', kwargs={
                'template_name': 'favorites/mymodel_list.html',
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


@login_required
def drop_favorite(request, object_id, redirect_to=None):
    Favorite.objects.filter(pk=object_id,
                            user=request.user).delete()
    if redirect_to:
        return redirect(redirect_to)
    else:
        return(request.META.get('HTTP_REFERER', 'favorites'))
