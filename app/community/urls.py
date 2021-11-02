from django.urls import path, include
from rest_framework import routers
from community import views

from . import views

router = routers.DefaultRouter()
router.register(r'nft', views.NftOwnership, basename="nft-ownership")
router.register(r'community', views.CommunityViewSet, basename="community")
router.register(r'communal_canvas', views.CommunalCanvasViewSet, basename="communal_canvas")
router.register(r'messages', views.MessagesViewSet, basename="messages")
router.register(r'contracts', views.ContractViewSet, basename="contract")

urlpatterns = [
    path('', include(router.urls)),
]
