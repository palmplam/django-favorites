from django import forms
from models import Favorite


class ObjectIdForm(forms.Form):
    object_id = forms.IntegerField(widget=forms.HiddenInput())


### FOLDER FORMS ###########################################################


class FolderForm(forms.Form):
    name = forms.CharField(max_length=100)


### FAVORITE FORMS #########################################################


class ObjectHiddenForm(forms.Form):
    """Form to confirm favorite creation"""
    app_label = forms.CharField(max_length=100,
                                widget=forms.HiddenInput())
    object_name = forms.CharField(max_length=100,
                                  widget=forms.HiddenInput())
    object_id = forms.IntegerField(widget=forms.HiddenInput())
