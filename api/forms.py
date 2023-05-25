# forms.py
from django import forms
from .models import client

class ClientForm(forms.ModelForm):
    class Meta:
        model = client
        fields = '__all__'
