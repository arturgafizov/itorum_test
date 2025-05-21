from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from apps.users  import views

app_name = 'apps.users'

router = DefaultRouter()


urlpatterns = [
    path('', login_required(RedirectView.as_view(pattern_name='admin:index'))),
    path('login/', views.LoginView.as_view(), name='api_pre-login'),
    path('register/', views.SignUpView.as_view(), name='api_sign_up'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]

urlpatterns += router.urls
