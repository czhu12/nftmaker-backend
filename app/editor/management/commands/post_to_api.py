from django.core.management.base import BaseCommand
import os
import requests
from users.models import *
from editor.models import *
from community.models import *
from editor.serializers import ProjectSerializer
from community.serializers import *
from rest_framework import serializers

class BigCommunalCanvasSerializer(serializers.ModelSerializer):
    pixels = PixelSerializer(read_only=True, many=True)
    created_at = serializers.SerializerMethodField('get_created_at')

    def get_created_at(self, obj):
        return obj.created.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Community
        fields = [
            'id', 'pixels', 'created_at'
        ]

class BigCommunitySerializer(serializers.ModelSerializer):
    messages = MessageSerializer(read_only=True, many=True)
    communal_canvas = BigCommunalCanvasSerializer(read_only=True, many=True)
    created_at = serializers.SerializerMethodField('get_created_at')

    def get_created_at(self, obj):
        return obj.created.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Community
        fields = [
            'id', 'slug', 'name', 'description', 'website', 'opensea',
            'twitter', 'discord', 'etherscan', 'contract', 'messages',
            'communal_canvas', 'created_at'
        ]


class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at')
    def get_created_at(self, obj):
        return obj.date_joined.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = User
        fields = ['username', 'email', 'is_superuser', 'created_at']


def build_project_json(project):
    serializer = ProjectSerializer(project)
    return serializer.data


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('endpoint', type=str)
        parser.add_argument('type', type=str)

    def handle(self, *args, **options):
        endpoint = options['endpoint']
        headers = { 'X-Authorization': os.environ.get('BACKFILL_SECRET') }
        if options['type'] == 'users':
            users = User.objects.all()
            for user in users:
                body = UserSerializer(user).data
                response = requests.post(endpoint + '/backfill_users', json=body, headers=headers)
                if response.status_code != 200:
                    raise Exception(response.text)

        if options['type'] == 'editor':
            projects = Project.objects.all()
            for project in projects:
                body = ProjectSerializer(project).data
                body['username'] = project.user.username
                response = requests.post(endpoint + '/backfill_editor', json=body, headers=headers)
                if response.status_code != 200:
                    raise Exception(response.text)

        if options['type'] == 'contracts':
            contracts = Contract.objects.all()
            for contract in contracts:
                body = ContractSerializer(contract).data
                response = requests.post(endpoint + '/backfill_contract', json=body, headers=headers)
                if response.status_code != 200:
                    raise Exception(response.text)

        if options['type'] == 'communities':
            communities = Community.objects.all()
            for community in communities:
                body = BigCommunitySerializer(community).data
                response = requests.post(endpoint + '/backfill_communities', json=body, headers=headers)
                if response.status_code != 200:
                    raise Exception(response.text)