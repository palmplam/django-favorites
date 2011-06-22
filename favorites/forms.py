from django import forms
from models import Favorite


class ObjectIdForm(forms.Form):
    object_id = forms.IntegerField(widget=forms.HiddenInput())


class ObjectHiddenForm(forms.Form):
    """Form to confirm favorite creation"""
    app_label = forms.CharField(max_length=100,
                                widget=forms.HiddenInput())
    object_name = forms.CharField(max_length=100,
                                  widget=forms.HiddenInput())
    object_id = forms.IntegerField(widget=forms.HiddenInput())


### FOLDER FORMS ###########################################################


class FolderForm(forms.Form):
    name = forms.CharField(max_length=100)


### FAVORITE FORMS #########################################################

class CreateFavoriteForm(ObjectHiddenForm):
    """Form to confirm favorite creation"""
    folder = forms.ChoiceField(required=True)

    def __init__(self, choices, **kwargs):
        forms.Form.__init__(self, **kwargs)
        self.fields['folder'].choices = choices


class UpdateFavoriteForm(ObjectIdForm):
    folder = forms.ChoiceField(required=True)
