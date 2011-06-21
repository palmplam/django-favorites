from django import forms
from models import Favorite


class CreateFavoriteHiddenForm(forms.Form):
    """Form to confirm favorite creation"""
    app_label = forms.CharField(max_length=100,
                                widget=forms.HiddenInput())
    object_name = forms.CharField(max_length=100,
                                  widget=forms.HiddenInput())
    object_id = forms.IntegerField(widget=forms.HiddenInput())


class DeleteFavoriteForm(forms.ModelForm):
    """
    base class for deleting favorite instance

    you may extend this form to provide additional
    validation rules (checkboxes, captcha, etc...)
    """

    class Meta:
        model = Favorite
        fields = ('id',)

    def save(self, commit=True):
        """
        Simply deletes bound instance and returns instance.
        If commit is set to False, does nothing.
        """

        if commit:
            self.instance.delete()
        return self.instance

