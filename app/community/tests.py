from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, force_authenticate

from community.models import Contract, Community, Message, CommunalCanvas, Pixel
from unittest.mock import patch
import factory
import json


class CommunityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Community

    name = factory.Sequence(lambda n: 'community-{}'.format(n))
    slug = factory.Sequence(lambda n: 'community-{}'.format(n))


class CommunalCanvasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommunalCanvas

    community = factory.SubFactory(CommunityFactory)
    image = {}


class PixelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pixel

    x = 0
    y = 0
    color = 0
    token_identifier = "1"
    communal_canvas = factory.SubFactory(CommunalCanvasFactory)


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    token_identifier = factory.Sequence(lambda n: '{}'.format(n))
    body = 'Hello world!'
    community = factory.SubFactory(CommunityFactory)


class ContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contract

    address = factory.Sequence(lambda n: '0x1234{}'.format(n))
    block_number = 100


def mock_moralis_nft_contract(address, chain=""):
    return {
        "token_address": address,
        "name": "OpenSea Collections",
        "symbol": "OPENSTORE",
        "abi": None,
        "contract_type": "ERC1155",
        "supports_token_uri": None,
        "synced_at": "2021-08-25"
    }


@patch('community.views._moralis_get_nft_contract',
       side_effect=mock_moralis_nft_contract)
class ContractViewTests(TestCase):
    def test_get_new_community_by_new_contract(self, _):
        response = self.client.get(
            reverse('community-detail', kwargs={
                'pk': '0x12345678',
            }))
        self.assertTrue(response.json()['name'] == 'OpenSea Collections')
        self.assertTrue('communal_canvas' in response.json())
        self.assertTrue(len(response.json()['messages']) == 0)

    def test_get_new_community_by_existing_contract(self, _):
        address = '0x123456789'
        ContractFactory.create(address=address)
        response = self.client.get(
            reverse('community-detail', kwargs={
                'pk': address,
            }))
        self.assertTrue(response.json()['name'] == address)
        self.assertTrue('communal_canvas' in response.json())
        self.assertTrue(len(response.json()['messages']) == 0)

    def test_get_messages(self, _):
        community = CommunityFactory.create()
        message_1 = MessageFactory.create(community=community)
        message_2 = MessageFactory.create(community=community)
        response = self.client.get(reverse('messages-list'),
                                   {'community': community.id})
        self.assertTrue(len(response.json()) == 2)

    def test_create_message(self, _):
        community = CommunityFactory.create()
        response = self.client.post(
            reverse('messages-list'),
            {
                'token_identifier': '1',
                'community': community.id,
                'body': 'Hello world!',
            },
        )
        self.assertTrue(response.status_code == 201)

    def test_create_contract(self, _):
        response = self.client.post(
            reverse('contract-list'),
            {
                'address': '0x12345',
                'balance': '10000',
                'block_number': 100,
                'block_timestamp': 10000,
                'contract_type': 'ERC721'
            },
        )
        response = response.json()
        self.assertTrue(response['address'] == '0x12345')
        self.assertTrue(response['block_timestamp'] == 10000)

        response = self.client.post(
            reverse('contract-list'),
            {
                'address': '0x12345',
                'balance': '10000',
                'block_number': 1001,
                'contract_type': 'ERC721'
            },
        )
        self.assertTrue(response.json()['block_number'] == 1001)
        self.assertTrue(response.json()['balance'] == '10000')
        self.assertTrue(len(Contract.objects.all()) == 1)
        response = self.client.post(
            reverse('contract-list'),
            {
                'address': '0x123466',
                'balance': '10000',
                'block_number': 1001,
                'contract_type': 'ERC721'
            },
        )
        self.assertTrue(len(Contract.objects.all()) == 2)


class PixelTests(TestCase):
    def test_list(self):
        communal_canvas = CommunalCanvasFactory.create()
        PixelFactory.create()
        PixelFactory.create(communal_canvas=communal_canvas)
        client = APIClient()
        response = client.get(
            reverse('pixels-list'),
            {
              'communal_canvas': communal_canvas.id,
            },
        )
        response.json()
        self.assertTrue(len(response.json()['results']) == 1)

    def test_post(self):
        communal_canvas = CommunalCanvasFactory.create()
        client = APIClient()
        response = client.post(
            reverse('pixels-list'),
            {
              'communal_canvas': communal_canvas.id,
              'color': 1200,
              'token_identifier': '1',
              'x': 0,
              'y': 0,
            },
        )
        response.json()
        communal_canvas.refresh_from_db()
        self.assertTrue(len(communal_canvas.image['data']), 1)
        self.assertTrue(len(communal_canvas.pixels.all()), 1)
        self.assertTrue(communal_canvas.image['data']['0']['0'] == 1200)


class MessageTests(TestCase):
    def test_list(self):
        pass


class ReplyTests(TestCase):
    def test_list(self):
        client = APIClient()
        message = MessageFactory.create()
        response = client.post(reverse('replies-list'), {
            'token_identifier': '1',
            'body': '12345',
            'message': message.id,
        })
        self.assertTrue(response.json()['body'] == '12345')
        self.assertTrue(response.json()['token_identifier'] == '1')
