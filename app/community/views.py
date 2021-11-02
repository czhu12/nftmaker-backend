from django.http import Http404
import os
from django.http.response import HttpResponse
import requests
from rest_framework import viewsets, status
from community.serializers import ContractSerializer, MessageSerializer
from community.models import Contract, Community, CommunalCanvas, Message
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from community.serializers import CommunitySerializer
from django.db import transaction

CHAIN = "rinkeby"


def _moralis_get_nft_contract(address):
    response = requests.get(
        'https://deep-index.moralis.io/api/v2/nft/{}/metadata?chain={}&format=decimal'
        .format(address, CHAIN),
        headers={
            'accept': 'application/json',
            'X-API-Key': os.environ.get('MORALIS_API_KEY')
        },
    )
    if response.status_code != 200:
        return HttpResponse(status=404)
    return response.json()


def create_community_for_contract(name, contract):
    community = Community(
        name=name,
        slug=contract.address,
        etherscan="https://etherscan.io/contract/{}".format(contract.address),
    )
    community.save()
    contract.community = community
    contract.save()

    communal_canvas = CommunalCanvas(community=community)
    communal_canvas.save()
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
            data = _moralis_get_nft_contract(pk)
            community = create_community_from_metadata(data)
        serializer = CommunitySerializer(community)
        return Response(serializer.data)


class CommunalCanvasViewSet(viewsets.ViewSet):
    def update(self, request, pk=None):
        contract = CommunalCanvas.objects.get(address=pk)
        return Response(serializer.data)


class MessagesViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def list(self, request):
        community_id = request.GET.get('community')
        if not community_id:
            raise Http404
        community = Community.objects.get(pk=community_id)
        serializer = self.get_serializer(community.messages, many=True)
        return Response(serializer.data)


class NftOwnership(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        response = requests.get(
            'https://deep-index.moralis.io/api/v2/{}/nft?chain={}&format=decimal'
            .format(pk, CHAIN),
            headers={
                'accept': 'application/json',
                'X-API-Key': os.environ.get('MORALIS_API_KEY')
            },
        )

        return JsonResponse(response.json())
