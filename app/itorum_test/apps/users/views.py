import logging

from django.contrib.auth import get_user_model
from django.contrib.auth import logout as django_logout
from django.utils.decorators import method_decorator
from dj_rest_auth import views as auth_views
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny


from apps.users import serializers
from apps.users.services import full_logout
from apps.users  import swagger_schemas as schemas
from apps.users .generators import get_tokens_for_user

User = get_user_model()

logger = logging.getLogger(__name__)


class ViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'put', 'delete')


class UserModelViewSet(ViewSet):
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignUpView(CreateAPIView):
    serializer_class = serializers.UserSignUpSerializer
    permission_classes = (AllowAny,)


class LoginView(GenericAPIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = (AllowAny,)

    @method_decorator(name='create', decorator=swagger_auto_schema(**schemas.login, ))
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('login')
        user = User.objects.get(email=email)
        return (
            Response(get_tokens_for_user(user), status=status.HTTP_200_OK)
        )


class LogoutView(auth_views.LogoutView):
    allowed_methods = ('POST', 'OPTIONS')

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def session_logout(self):
        django_logout(self.request)

    def logout(self, request):
        self.session_logout()
        response = full_logout(request)
        return response
