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
from users.models import User
from rest_framework import pagination
from django.http import JsonResponse
from django.db.models.functions import TruncDay
from django.db.models import Count
from datetime import datetime, timedelta
from django.contrib.postgres.search import SearchVector


class ProjectPagination(pagination.PageNumberPagination):
       page_size = 5


class ProjectViewSet(viewsets.ModelViewSet):
    """
    GET /projects
    POST /projects
    GET /projects/1
    DELETE /projects/1
    """
    pagination_class = ProjectPagination
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ProjectPermissions]

    def get_queryset(self):
        projects = None
        if self.action == 'list' or self.action == 'retrieve':
            if self.request.GET.get('filter') == 'public' or self.request.user.is_anonymous:
                projects = Project.objects.filter(ispublic=True, listed=True).order_by('-modified')
            elif self.request.GET.get('filter') == 'own':
                projects = Project.objects.filter(user=self.request.user).order_by('-modified')
            elif self.request.user.is_superuser:
                projects = Project.objects.order_by('-modified')
            else:
                projects = Project.objects.filter((Q(ispublic=True) | Q(listed=True)) | Q(user=self.request.user)).order_by('-modified')

            if self.request.GET.get('q'):
                projects = projects.annotate(search=SearchVector('name')).filter(search=self.request.GET.get('q'))
        else:
            projects = self.request.user.projects.order_by('-modified')

        return projects

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        project = get_object_or_404(queryset, pk=pk)
        if (not project.listed) and (request.user != project.user) and not request.user.is_superuser:
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


def _statstics_for_model(model_class, key='created'):
    filters = {}
    filters[key + "__gte"] = datetime.now()-timedelta(days=7)
    stats = model_class.objects.filter(
            **filters
        ).annotate(
            day=TruncDay(key)
        ).values('day').annotate(c=Count('id')).values('day', 'c')
    count = model_class.objects.count()

    return [list(stats), count]

def statistics_view(request):
    project_stats, project_count = _statstics_for_model(Project)
    asset_stats, asset_count = _statstics_for_model(Asset)
    user_stats, user_count = _statstics_for_model(User, key='date_joined')

    return JsonResponse({
        'artists': { 'stats': user_stats, 'count': user_count },
        'projects': { 'stats': project_stats, 'count': project_count },
        'images': { 'stats': asset_stats, 'count': asset_count },
    })
