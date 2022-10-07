from django.contrib import admin
from .forms import CreateItemForm
from .models import Item, calc_size
from django.core.exceptions import ValidationError

# @admin.register(Item)
# class ItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'type', 'url', 'date', 'parent', 'size')
    
#     def get_readonly_fields(self, request, obj = None):
#         if obj:
#             return ['id']
#         return []
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
        result = super().get_form(request, obj=obj, **kwargs)
        self.form = orig_self_form
        return result