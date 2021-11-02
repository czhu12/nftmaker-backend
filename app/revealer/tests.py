from django.test import TestCase
from django.urls import reverse
from revealer.models import NftReveal
import factory
from unittest.mock import patch


class NftRevealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NftReveal

    slug = factory.Sequence(lambda n: 'nft-{}'.format(n))
    contract_address = factory.Sequence(lambda n: '0x12345{}'.format(n))


def mocked_s3_metadata(nft_reveal, token_id):
    return {
        "dna": "45e240b0b05aa88c4f70c7e07af0e2d1d1abed1c",
        "name": "#0",
        "description": "Dope Dinos",
        "image": "/images/0.png",
        "edition": 0,
        "date": 1634112372805,
        "attributes": [],
        "compiler": "compiler",
    }


@patch('revealer.views._reveal_metadata', side_effect=mocked_s3_metadata)
class RevealerViewTests(TestCase):
    def test_nft_revealed_metadata(self, _):
        nft_revealer = NftRevealFactory.create()

        response = self.client.get(
            reverse('metadata',
                    kwargs={
                        'slug': nft_revealer.slug,
                        'token_id': 0
                    }), )
        self.assertTrue(response.json()['description'] == "Dope Dinos")

    def test_nft_fake_metadata(self, _):
        nft_revealer = NftRevealFactory.create()

        response = self.client.get(
            reverse('metadata',
                    kwargs={
                        'slug': nft_revealer.slug,
                        'token_id': 100
                    }), )
        self.assertTrue("Pre-Reveal" in response.json()['description'])
        self.assertTrue("/revealer/nft-0/100.png" in response.json()['image'])
