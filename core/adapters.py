from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
from .models import CustomUser

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        # Set the default user type to 'mentee'
        user.user_type = 'mentee'
        return super().save_user(request, user, form, commit)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        # Extract username, first name, and last name from email
        email = data.get('email')
        name = data.get('name', '').split()  # Split to separate first and last name
        
        # Set username to the portion before '@' in the email
        username = slugify(email.split('@')[0])
        
        # Check for duplicate usernames and handle conflicts
        counter = 1
        original_username = username
        while CustomUser.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1

        # Assign values to user instance
        user = super().populate_user(request, sociallogin, data)
        user.username = username
        user.first_name = name[0] if name else ''
        user.last_name = name[1] if len(name) > 1 else ''
        user.user_type = 'mentee'  # Default user type to 'mentee'
        return user
