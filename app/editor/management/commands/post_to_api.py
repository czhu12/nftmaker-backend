from django.core.management.base import BaseCommand
import threading, time, random

from queue import Queue

import tqdm
import os
import requests
from users.models import *
from editor.models import *
from community.models import *
from editor.serializers import ProjectSerializer
from community.serializers import *
from rest_framework import serializers
import json
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


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
        jobs = Queue()
        pbar = tqdm.tqdm()

        def do_send(q):
            while not q.empty():
                value = q.get()
                body = value['serializer_class'](value['model']).data
                if value['serializer_class'] == ProjectSerializer:
                    print(value['model'].user.username)
                    body['username'] = value['model'].user.username
                response = requests.post(value['endpoint'], json=json.loads(json.dumps(body, cls=UUIDEncoder)), headers=headers)
                pbar.update()
                if response.status_code != 200:
                    raise Exception(response.text)
                q.task_done()

        if options['type'] == 'users':
            users = User.objects.all()
            for user in users:
                value = {
                  'serializer_class': UserSerializer,
                  'model': user,
                  'endpoint': endpoint + '/backfill_users',
                }
                jobs.put(value)

        if options['type'] == 'editor':
            projects = Project.objects.all()
            for project in projects:
                value = {
                  'serializer_class': ProjectSerializer,
                  'model': project,
                  'endpoint': endpoint + '/backfill_editor',
                }
                jobs.put(value)

        if options['type'] == 'contracts':
            contracts = Contract.objects.all()
            for contract in contracts:
                value = {
                  'serializer_class': ContractSerializer,
                  'model': contract,
                  'endpoint': endpoint + '/backfill_contract',
                }
                jobs.put(value)

        if options['type'] == 'communities':
            communities = Community.objects.all()
            for community in communities:
                value = {
                  'serializer_class': BigCommunitySerializer,
                  'model': community,
                  'endpoint': endpoint + '/backfill_communities',
                }
                jobs.put(value)

        for i in range(10):
            worker = threading.Thread(target=do_send, args=(jobs,))
            worker.start()

        pbar.total = jobs.qsize()
        print("waiting for queue to complete", jobs.qsize(), "tasks")
        jobs.join()

