from django.test import TestCase
from django.urls import reverse
from revealer.models import NftReveal
import factory

class NftRevealFactory(factory.django.DjangoModelFactory):
  class Meta:
      model = NftReveal

  slug = factory.Sequence(lambda n: 'nft-{}'.format(n))
  contract_address = factory.Sequence(lambda n: '0x12345{}'.format(n))

class RevealerViewTests(TestCase):

    def test_nft_revealer_metadata(self):
        nft_revealer = NftRevealFactory.create()
    
        response = self.client.get(
          reverse('metadata', kwargs={'slug': nft_revealer.slug, 'token_id': 100}),
        )
        self.assertTrue("Pre-Reveal" in response.json()['description'])
        self.assertTrue("/revealer/nft-0/100.png" in response.json()['image'])
