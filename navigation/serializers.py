# navigation/serializers.py
from rest_framework import serializers
from .models import MenuItem, NavigationSettings

class MenuItemSerializer(serializers.ModelSerializer):
    submenus = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['title', 'url', 'is_button', 'submenus']

    def get_submenus(self, obj):
        submenus = obj.submenus.all().order_by('order')
        return MenuItemSerializer(submenus, many=True).data

class NavigationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationSettings
        fields = ['normal_logo', 'sticky_logo']
