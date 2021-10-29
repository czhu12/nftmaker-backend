
from django.urls import path

from . import views

urlpatterns = [
    path('<str:slug>/<int:token_id>.png', views.image, name='image'),
    path('<str:slug>/<int:token_id>', views.metadata, name='metadata'),
]