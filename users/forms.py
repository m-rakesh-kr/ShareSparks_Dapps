from django.contrib.auth.forms import UserCreationForm
from django import forms

from users.models import CustomUser


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        error_messages = {
            'username': {'invalid': 'Username may only contain letters, numbers, and @/./+/-/_ characters.'},
        }


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField()


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_image', 'contact_number']


class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['is_active']
