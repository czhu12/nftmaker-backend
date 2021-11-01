from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, force_authenticate

from editor.models import Group, User, Project
from users.models import User
import factory


class ContractViewTests(TestCase):
    def test_create_contract(self):
        # First create the user
        response = self.client.post(
            reverse('contract-list'),
            {'address': '0x12345', 'block_number': 100, 'contract_type': 'ERC721'},
        )
        response = response.json()
        self.assertTrue(response['address'] == '0x12345')