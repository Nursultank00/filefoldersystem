from django.contrib import admin
from .forms import CreateItemForm, UpdateItemForm
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'url', 'date', 'parent', 'size')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['id', 'type']
        else:
            return []

    def get_form(self, request, obj=None, **kwargs):
        orig_self_form = self.form
        if not obj:
            self.form = CreateItemForm
        if obj:
            self.form = UpdateItemForm
        result = super().get_form(request, obj=obj, **kwargs)
        self.form = orig_self_form
        return result