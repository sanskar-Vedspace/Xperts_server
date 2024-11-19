def set_user_type(backend, user, response, *args, **kwargs):
    if not user.user_type:
        user.user_type = 'mentee'
        user.save()
