from django.forms.models import ModelForm
from business.models import Address
from django import forms

class AddressForm(ModelForm):
  class Meta:
    model = Address
    fields = ['address_type', 'apartment_number', 'street', 'distric', 'city_or_province', 'phone',]