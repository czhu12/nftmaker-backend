from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'groups', views.GroupViewSet)
router.register(r'layers', views.LayerViewSet)
router.register(r'assets', views.AssetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
