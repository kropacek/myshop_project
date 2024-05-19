from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import CustomUser
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50, label=_('Email'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password2 = forms.CharField(widget=forms.PasswordInput, label=_('Re-enter password'))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'second_name', 'email']
        labels = {'first_name': _('First name'),
                  'second_name': _('Second name'),
                  'email': _('Email')}

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError(_('Passwords don\'t match.'))
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email']

        if CustomUser.objects.filter(email=data).exists():
            raise forms.ValidationError(_('Email already in use.'))
        return data


class EditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'second_name', 'date_of_birth', 'city', 'address', 'postal_code']
        labels = {'first_name': _('First name'),
                  'second_name': _('Second name'),
                  'date_of_birth': _('Date of birth'),
                  'city': _('City'),
                  'address': _('Address'),
                  'postal_code': _('Postal code')}
        widgets = {'date_of_birth': forms.NumberInput(attrs={'type': 'date'})}


class CustomPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].help_text = ''
        self.fields['new_password1'].help_text = ''
        self.fields['new_password2'].help_text = ''


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )