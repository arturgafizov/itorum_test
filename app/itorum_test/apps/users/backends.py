from django.contrib.auth import get_user_model


class EmailBackend(object):
    """
    Custom Phone or Email Backend to perform authentication via phone or email
    """

    def authenticate(self, login=None, password=None):
        my_user_model = get_user_model()
        try:
            user = my_user_model.objects.get(email=login)
            if user.check_password(password):
                return user
        except my_user_model.DoesNotExist:
            return None
