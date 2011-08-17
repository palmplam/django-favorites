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


class FolderForm(forms.Form):
    name = forms.CharField(max_length=100)


class UserFolderChoicesForm(forms.Form):
    """Form to confirm favorite creation"""

    def __init__(self, choices, **kwargs):
        super(UserFolderChoicesForm, self).__init__(**kwargs)
        self.fields['folder_id'] = EmptyChoiceField(required=False,
                                                    label=_("Store in a folder?"),
                                                    empty_label=_("No folder"),
                                                    choices=choices,
                                                    initial=kwargs.get('folder_id', None))



class ValidationForm(forms.Form):
    pass

class HiddenFolderForm(forms.Form):
    folder_id = forms.IntegerField(widget=forms.HiddenInput())
