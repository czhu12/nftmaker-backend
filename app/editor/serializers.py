from editor.models import Project, Group, Layer, Asset
from community.serializers import ContractSerializer
from rest_framework import serializers


class AssetSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at')
    def get_created_at(self, obj):
        return obj.created.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Asset
        fields = ['id', 'name', 'rarity', 'image_file', 'layer', 'created_at']


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
    contract = ContractSerializer(read_only=True)
    created_at = serializers.SerializerMethodField('get_created_at')

    def create(self, validated_data):
        project = Project.objects.create(
            name=validated_data['name'],
            user=self.context['request'].user
        )

        return project

    def get_created_at(self, obj):
        return obj.created.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'website', 'opensea', 'twitter',
            'discord', 'etherscan', 'width', 'height', 'ispublic', 'listed',
            'groups', 'contract', 'created_at'
        ]
