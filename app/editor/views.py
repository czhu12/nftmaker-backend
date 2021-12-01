from django.http import HttpResponse
from django.db.models import Q
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
from editor.permissions import OwnDataPermission, ProjectPermissions

class ProjectViewSet(viewsets.ModelViewSet):
    """
    GET /projects
    POST /projects
    GET /projects/1
    DELETE /projects/1
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ProjectPermissions]

    def get_queryset(self):
        import pdb;pdb.set_trace()
        if self.action == 'list' or self.action == 'retrieve':
            if self.request.GET.get('filter') == 'public' or self.request.user.is_anonymous:
                return Project.objects.filter(ispublic=True, listed=True)
            elif self.request.GET.get('filter') == 'own':
                return Project.objects.filter(user=self.request.user)
            else:
                return Project.objects.filter((Q(ispublic=True) & Q(listed=True)) | Q(user=self.request.user))
        else:
            return self.request.user.projects

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        project = get_object_or_404(queryset, pk=pk)
        if not project.ispublic and request.user != project.user:
            return Response("FORBIDDEN", status=status.HTTP_403_FORBIDDEN)

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
    permission_classes = [permissions.IsAuthenticated, OwnDataPermission]


class LayerViewSet(viewsets.ViewSetMixin, CreateAPIView, UpdateModelMixin, DestroyModelMixin):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer
    permission_classes = [permissions.IsAuthenticated, OwnDataPermission]


class AssetViewSet(viewsets.ViewSetMixin, CreateAPIView, UpdateModelMixin, DestroyModelMixin):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [permissions.IsAuthenticated, OwnDataPermission]
