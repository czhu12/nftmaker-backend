from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.response import Response
from editor.models import Project, Group, Layer, Asset
from editor.serializers import ProjectSerializer, GroupSerializer, LayerSerializer, AssetSerializer
from rest_framework.viewsets import ViewSetMixin, ModelViewSet
from rest_framework import parsers

class ProjectViewSet(viewsets.ModelViewSet):
    """
    GET /projects
    POST /projects
    GET /projects/1
    DELETE /projects/1
    """
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.GET.get('filter') == 'all' or self.request.user.is_anonymous:
            return Project.objects.filter(ispublic=True, listed=True)
        else:
            user = self.request.user
            return Project.objects.filter(user=user)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        project = get_object_or_404(queryset, pk=pk)
        if not project.ispublic and request.user is None or request.user != project.user:
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.user = request.user
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GroupViewSet(viewsets.ViewSetMixin, CreateAPIView, UpdateModelMixin, DestroyModelMixin):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class LayerViewSet(viewsets.ViewSetMixin, CreateAPIView, UpdateModelMixin, DestroyModelMixin):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer
    permission_classes = [permissions.IsAuthenticated]


class AssetViewSet(viewsets.ViewSetMixin, CreateAPIView, UpdateModelMixin, DestroyModelMixin):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [permissions.IsAuthenticated]
