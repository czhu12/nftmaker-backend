import json
from django.http import Http404
from django.core.cache import cache
import os
from django.http.response import HttpResponse
import requests
from rest_framework import viewsets, status, permissions
from community.serializers import ContractSerializer, MessageSerializer, CommunalCanvasSerializer, ReplySerializer, PixelSerializer
from community.models import Contract, Community, CommunalCanvas, Message, Reply, Pixel
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from community.serializers import CommunitySerializer
from django.db import transaction

DEFAULT_CHAIN = "eth"

def _moralis_get_nft_contract(address, chain=DEFAULT_CHAIN):
    response = requests.get(
        'https://deep-index.moralis.io/api/v2/nft/{}/metadata?chain={}&format=decimal'
        .format(address, CHAIN),
        headers={
            'accept': 'application/json',
            'X-API-Key': os.environ.get('MORALIS_API_KEY')
        },
    )
    if response.status_code != 200:
        raise Http404
    return response.json()


def create_community_for_contract(name, contract):
    try:
        community = Community.objects.get(slug=contract.address)
    except Community.DoesNotExist:
        community = Community(
            name=name,
            slug=contract.address,
            etherscan="https://etherscan.io/contract/{}".format(contract.address),
        )
        community.save()
        communal_canvas = CommunalCanvas(community=community)
        communal_canvas.save()

    contract.community = community
    contract.save()

    return community


@transaction.atomic
def create_community_from_metadata(data):
    contract = Contract(address=data['token_address'],
                        contract_type=data['contract_type'],
                        symbol=data['symbol'])
    contract.save()
    community = create_community_for_contract(data['name'], contract)
    return community


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.order_by('-block_number')
    serializer_class = ContractSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            contract = Contract.objects.get(
                address=serializer.validated_data['address'])
            contract.__dict__.update(**serializer.validated_data)
            contract.save()
        except Contract.DoesNotExist:
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class CommunityViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        try:
            contract = Contract.objects.get(address=pk)
            community = contract.community
            if not community:
                community = create_community_for_contract(contract.address, contract)
        except Contract.DoesNotExist:
            chain = self.request.GET.get('chain', DEFAULT_CHAIN)
            data = _moralis_get_nft_contract(pk, chain=chain)
            community = create_community_from_metadata(data)
        serializer = CommunitySerializer(community)
        return Response(serializer.data)


class PixelViewSet(viewsets.ModelViewSet):
    serializer_class = PixelSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        pixel = serializer.save()
        communal_canvas = pixel.communal_canvas
        image = communal_canvas.image
        x = str(pixel.x)
        y = str(pixel.y)
        if not image:
            image = {'data': {}}
        if not x in image['data']:
            image['data'][x] = {}
        image['data'][x][y] = pixel.color
        communal_canvas.image = image
        communal_canvas.save()
        return pixel

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        communal_canvas_id = self.request.GET.get('communal_canvas')
        if communal_canvas_id is None:
            raise Http404("Must include communal_canvas")
        return Pixel.objects.filter(communal_canvas_id=communal_canvas_id).order_by('-created')


class RepliesViewSet(viewsets.ModelViewSet):
    serializer_class = ReplySerializer


class MessagesViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def list(self, request):
        community_id = request.GET.get('community')
        if not community_id:
            raise Http404
        community = Community.objects.get(pk=community_id)
        serializer = self.get_serializer(community.messages.order_by('-created'), many=True)
        return Response(serializer.data)


def retrieve_cached_json(cache_key, fetch, force=False, expiration=600):
    cached = cache.get(cache_key)
    if not cached or force:
        data = fetch()
        cache.set(cache_key, json.dumps(data))
        return data
    else:
        return json.loads(cached)


class NftOwnership(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        chain = self.request.GET.get('chain', DEFAULT_CHAIN)
        cache_key = f'NFTOwnership-retrieve-{pk}-{chain}'
        def _fetch():
            response = requests.get(
                'https://deep-index.moralis.io/api/v2/{}/nft?chain={}&format=decimal'
                .format(pk, chain),
                headers={
                    'accept': 'application/json',
                    'X-API-Key': os.environ.get('MORALIS_API_KEY')
                },
            )
            data = response.json()
            return data

        data = retrieve_cached_json(cache_key, _fetch)


        return JsonResponse(data)
