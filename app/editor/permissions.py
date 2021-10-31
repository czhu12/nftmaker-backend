from rest_framework import permissions
from editor import models


def validate_project_by_id(project_id, request):
    project = models.Project.objects.get(pk=project_id)
    return project.user == request.user


def validate_group_by_id(group_id, request):
    group = models.Group.objects.get(pk=group_id)
    return group.project.user == request.user


def validate_layer_by_id(layer_id, request):
    layer = models.Layer.objects.get(pk=layer_id)
    return layer.group.project.user == request.user


def validate_asset_by_id(asset_id, request):
    asset = models.Asset.objects.get(pk=asset_id)
    return asset.layer.group.project.user == request.user


class OwnDataPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action == 'create':
            project_id = request.data.get('project')
            if project_id:
                return validate_project_by_id(project_id, request)

            group_id = request.data.get('group')
            if group_id:
                return validate_group_by_id(group_id, request)

            layer_id = request.data.get('layer')
            if layer_id:
                return validate_layer_by_id(layer_id, request)

            asset_id = request.data.get('asset')
            if asset_id:
                return validate_asset_by_id(asset_id, request)
        else:
            view_name = view.__class__.__name__
            _id = view.kwargs.get('pk')
            if view_name == 'ProjectViewSet':
                return validate_project_by_id(_id, request)
            if view_name == 'GroupViewSet':
                return validate_group_by_id(_id, request)
            if view_name == 'LayerViewSet':
                return validate_layer_by_id(_id, request)
            if view_name == 'AssetViewSet':
                return validate_asset_by_id(_id, request)
        return True
