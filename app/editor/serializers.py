from editor.models import Project, Group, Layer, Asset
from rest_framework import serializers


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name', 'rarity', 'image_file', 'layer']


class LayerSerializer(serializers.ModelSerializer):
    assets = AssetSerializer(many=True, read_only=True)

    class Meta:
        model = Layer
        fields = ['id', 'name', 'rarity', 'group', 'order', 'assets']


class GroupSerializer(serializers.ModelSerializer):
    layers = LayerSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'layers', 'project']


class ProjectSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    def create(self, validated_data):
        project = Project.objects.create(
            name=validated_data['name'],
            user=self.context['request'].user
        )

        return project

    class Meta:
        model = Project
        fields = ['id', 'name', 'width', 'height', 'ispublic', 'listed', 'groups']
