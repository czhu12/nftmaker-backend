from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import views


urlpatterns = [
    path('me/', views.UserView.as_view(), name='me'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('nonce-auth/', views.obtain_auth_token_via_nonce, name='nonce_auth'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
]
