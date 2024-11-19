from rest_framework.permissions import BasePermission

class IsPremiumSubscriber(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a mentee and has an active subscription
        if request.user.is_authenticated and hasattr(request.user, 'subscription'):
            return request.user.subscription.is_active
        return False
