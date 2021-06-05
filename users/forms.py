from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
  phone = forms.CharField()

class CustomUserCreationForm2(UserCreationForm):
  phone = forms.CharField()
  class Meta(UserCreationForm.Meta):
    fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name",)