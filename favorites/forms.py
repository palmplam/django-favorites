from django import forms
from models import Favorite


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

class CreateFavoriteForm(ObjectHiddenForm):
    """Form to confirm favorite creation"""
    folder = forms.ChoiceField(required=True)

    def __init__(self, choices, **kwargs):
        super(CreateFavoriteForm, self).__init__(**kwargs)
        self.fields['folder'].choices = choices
        self.fields['folder'].length = len(choices)


class UpdateFavoriteForm(ObjectIdForm):
    folder = forms.ChoiceField(required=True)

    def __init__(self, choices, **kwargs):
        super(UpdateFavoriteForm, self).__init__(**kwargs)
        self.fields['folder'].choices = choices


class FavoriteMoveHiddenForm(ObjectIdForm):
    folder = forms.CharField(widget=forms.HiddenInput(),
                             required=True)


class ValidationForm(forms.Form):
    pass
