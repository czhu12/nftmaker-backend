import os
from django.http.response import HttpResponse
import requests
from rest_framework import viewsets
from community.models import Contract, Community, CommunalCanvas
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from community.serializers import CommunitySerializer
from django.db import transaction


CHAIN = "rinkeby"

@transaction.atomic
def create_community_from_metadata(data):
  """
  {
  "token_address": "0x88b48f654c30e99bc2e4a1559b4dcf1ad93fa656",
  "name": "OpenSea Collections",
  "symbol": "OPENSTORE",
  "abi": null,
  "contract_type": "ERC1155",
  "supports_token_uri": null,
  "synced_at": "2021-08-25"
  }
  """
  community = Community(
    name=data['name'],
    slug=data['token_address'],
    etherscan="https://etherscan.io/contract/{}".format(data['token_address']),
  )
  community.save()
  contract = Contract(
    address=data['token_address'],
    contract_type=data['contract_type'],
    symbol=data['symbol'],
    community=community
  )
  contract.save()
  communal_canvas = CommunalCanvas(community=community)
  communal_canvas.save()
  return community

class CommunityViewSet(viewsets.ViewSet):
    queryset = Contract.objects.all()
    def retrieve(self, request, pk=None):
        try:
            contract = Contract.objects.get(address=pk)
            community = contract.community
        except Contract.DoesNotExist:
            response = requests.get(
              'https://deep-index.moralis.io/api/v2/nft/{}/metadata?chain={}&format=decimal'.format(pk, CHAIN),
              headers={'accept': 'application/json', 'X-API-Key': os.environ.get('MORALIS_API_KEY')},
            )
            if response.status_code != 200:
              return HttpResponse(status=404)
            community = create_community_from_metadata(response.json())
        serializer = CommunitySerializer(community)
        return Response(serializer.data)


class NftOwnership(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        response = requests.get(
          'https://deep-index.moralis.io/api/v2/{}/nft?chain={}&format=decimal'.format(pk, CHAIN),
          headers={'accept': 'application/json', 'X-API-Key': os.environ.get('MORALIS_API_KEY')},
        )

        return JsonResponse(response.json())
