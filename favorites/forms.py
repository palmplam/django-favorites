from django import forms
from django.utils.translation import ugettext_lazy as _

from models import Favorite

class EmptyChoiceField(forms.ChoiceField):
    """
    Utils to make more easy and DRY to manage an empty label when needed.
    """
    def __init__(self, choices=(), empty_label="-----", required=True,
        widget=None, label=None, initial=None, help_text=None, *args, **kwargs):

        # add an empty label if it exists (and field is not required!)
        if not required:
            choices = tuple([(u'', empty_label)] + list(choices))

        super(EmptyChoiceField, self).__init__(choices=choices, required=required,
                 widget=widget, label=label, initial=initial, help_text=help_text,
                                                                  *args, **kwargs)

class ObjectIdForm(forms.Form):
    object_id = forms.IntegerField(widget=forms.HiddenInput())

class ObjectHiddenForm(forms.Form):
    """Form to confirm favorite creation"""
    app_label = forms.CharField(max_length=100,
                                widget=forms.HiddenInput(),
                                required=True)
    object_name = forms.CharField(max_length=100,
                                  widget=forms.HiddenInput(),
                                  required=True)
    object_id = forms.IntegerField(widget=forms.HiddenInput(),
                                   required=True)


### FOLDER FORMS ###########################################################


class FolderForm(forms.Form):
    name = forms.CharField(max_length=100)


### FAVORITE FORMS #########################################################

class CreateFavoriteForm(forms.Form):
    """Form to confirm favorite creation"""
    folder = EmptyChoiceField(required=False,
                              label=_("Store in a folder?"),
                              empty_label=_("No folder"))
    def __init__(self, choices, **kwargs):
        super(CreateFavoriteForm, self).__init__(**kwargs)
        self.fields['folder'].choices = choices

class UpdateFavoriteForm(ObjectIdForm):

    def __init__(self, choices, **kwargs):
        super(UpdateFavoriteForm, self).__init__(**kwargs)
        self.fields['folder'] = EmptyChoiceField(
                                    required=False,
                                    label=_("Store in a folder?"),
                                    empty_label=_("No folder"),
                                    choices=choices,
                                )


class FavoriteMoveHiddenForm(ObjectIdForm):
    folder = forms.CharField(widget=forms.HiddenInput(),
                             required=True)


class ValidationForm(forms.Form):
    pass
