from editor.models import Project, Group, Layer, Asset
from rest_framework import serializers


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name', 'rarity', 'image_file']


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

    # def create(self, validated_data):
    #     group = Group.objects.create(
    #         name=validated_data['name'],
    #         project_id=self.context['view'].kwargs.get('project_id')
    #     )
    #     return group
    #
    # def update(self, instance, validated_data):
    #     import pdb; pdb.set_trace()
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.project_id = self.context['view'].kwargs.get('project_id')
    #     instance.save()
    #     return instance


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
        fields = ['id', 'name', 'groups']
