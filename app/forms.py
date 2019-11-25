from django import forms
from django.contrib.auth.models import User
from swapit_app.models import *
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('address', 'balance')


from django.forms import ModelForm, TextInput

class HomepageBannerForm(ModelForm):
    class Meta:
        model = HomepageBanner
        fields = '__all__'
        widgets = {
            'title_color': TextInput(attrs={'type': 'color'}),
            'subtitle_color': TextInput(attrs={'type': 'color'}),
            'button_text_color': TextInput(attrs={'type': 'color'}),
            'button_color': TextInput(attrs={'type': 'color'}),
        }
