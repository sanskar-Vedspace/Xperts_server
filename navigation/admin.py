# navigation/admin.py
from django.contrib import admin
from .models import MenuItem,NavigationSettings

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'parent', 'order', 'is_button')
    list_editable = ('order', 'is_button')
class NavigationSettingsAdmin(admin.ModelAdmin):
    pass
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(NavigationSettings, NavigationSettingsAdmin)
