from random import choices
from django import forms 
from django.forms import ValidationError

from .models import Item, ITEM_TYPE

class CreateItemForm(forms.ModelForm):
    new_id = forms.UUIDField(label = 'id')
    new_type = forms.ChoiceField(choices = ITEM_TYPE, label = 'type')
    new_size = forms.IntegerField(label = 'size')
    new_url = forms.CharField(max_length = 255, label = 'url', required = False)
    new_parent = forms.UUIDField(label = 'parent', required = False)

    def clean_new_id(self):
        code = self.cleaned_data['new_id']
        exists = Item.objects.filter(id = code)
        if exists:
            raise ValidationError("Entity with this name already exists: {}".format(exists))
        return code

    def save(self, commit=True):
        self.instance.id     = self.cleaned_data['new_id']
        self.instance.type   = self.cleaned_data['new_type']
        self.instance.parent = self.cleaned_data['new_parent']
        self.instance.size   = self.cleaned_data['new_size']
        self.instance.url    = self.cleaned_data['new_url']
        return super().save(commit)
        
        
    class Meta:
        model = Item
        fields = ['new_id', 'new_type', 'new_size', 'new_url', 'new_parent']
