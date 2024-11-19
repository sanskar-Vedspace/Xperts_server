# navigation/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from .models import MenuItem, NavigationSettings
from .serializers import MenuItemSerializer, NavigationSettingsSerializer

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow all users (authenticated or not) to access this view
def menu_list(request):
    # Get the menu items
    menus = MenuItem.objects.filter(parent__isnull=True).order_by('order')
    menu_serializer = MenuItemSerializer(menus, many=True)

    # Get the navigation settings (for logos)
    settings = NavigationSettings.objects.first()

    if settings:
        logos = {
            'normal_logo': request.build_absolute_uri(settings.normal_logo.url),
            'sticky_logo': request.build_absolute_uri(settings.sticky_logo.url),
        }
    else:
        logos = {'normal_logo': '', 'sticky_logo': ''}

    return Response({
        'menu': menu_serializer.data,
        'logos': logos
    })
