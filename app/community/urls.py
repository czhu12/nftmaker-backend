from django.urls import path, include
from rest_framework import routers
from community import views

from . import views

router = routers.DefaultRouter()
router.register(r'nft', views.NftOwnership, basename="nft-ownership")
router.register(r'', views.CommunityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
