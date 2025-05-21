from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.users.services import UsersService
from apps.users.backends import EmailBackend


User = get_user_model()

error_messages = {
    'not_verified': _('Email not verified'),
    'not_active': _('Your account is not active. Please contact Your administrator'),
    'wrong_credentials': _('Entered email or password is incorrect'),
}


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('keyword', 'email', 'username', )


class UserSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=2, max_length=100, required=True)
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    keyword = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password1', 'password2', 'keyword')

    def validate_password1(self, password: str) -> str:
        validate_password(password)
        return password

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password2': _("The two password fields didn't match.")})
        username = data['username']
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': _(f'User is already exist with username - {username}')})
        return data

    def save(self):
        self.validated_data['password'] = self.validated_data.pop('password1')
        del self.validated_data['password2']
        user = User.objects.create_user(**self.validated_data, is_active=False)
        UsersService.make_user_active(user)
        return user


class LoginSerializer(serializers.Serializer):
    login = serializers.EmailField(min_length=2, max_length=100, required=True)
    password = serializers.CharField(max_length=128)

    def validate(self, attrs: dict):
        self.user = self.authenticate(login=attrs['login'], password=attrs['password'])
        if self.user is None:
            raise serializers.ValidationError({'Error': _("The credentials is invalid")})
        if not self.user.is_active:
            raise serializers.ValidationError({'Error': _("The user is not active")})
        return attrs

    def authenticate(self, **kwargs):
        back = EmailBackend()
        return back.authenticate(**kwargs)