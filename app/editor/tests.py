from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, force_authenticate
from editor.services import ConnectContractWithProject

from editor.models import Group, User, Project
from users.models import User
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'chris{}'.format(n))
    email = factory.Sequence(lambda n: 'chris{}@example.com'.format(n))


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = 'Project'
    ispublic = False
    user = factory.SubFactory(UserFactory)


class ConnectContractWithProjectTests(TestCase):
    def test_create_contract(self):
        project = ProjectFactory.create(ispublic=True, listed=True)
        address = "0xffffff"
        ConnectContractWithProject(address, project).execute()
        project.refresh_from_db()
        self.assertTrue(project.contract.address == address)


class ProjectScopeTests(TestCase):
    def test_public_projects(self):
        project = ProjectFactory.create(ispublic=True, listed=True)
        client = APIClient()
        response = client.get(reverse('project-list'), {'filter': 'all'})
        self.assertTrue(len(response.json()['results']) == 1)


    def test_private_projects(self):
        ProjectFactory.create(ispublic=False, listed=False)
        ProjectFactory.create(ispublic=True, listed=False)
        client = APIClient()
        response = client.get(reverse('project-list'), {'filter': 'all'})
        self.assertTrue(len(response.json()['results']) == 0)


class PermissionsTests(TestCase):
    def _create_user(self):
        response = self.client.post(
            reverse('auth_register'),
            {
                'username': 'chris',
                'email': 'chris@example.com',
                'password': 'SecretPassword!',
                'password_confirmation': 'SecretPassword!'
            },
        )
        return response.json()['token']

    def test_forbidden_group_create(self):
        project = ProjectFactory.create()
        client = APIClient()
        token = self._create_user()
        response = client.post(
            reverse('group-list'),
            {'name': 'Group', 'project': project.id},
            HTTP_AUTHORIZATION='Token ' + token,
        )
        self.assertTrue(response.status_code == 403)

    def test_forbidden_project_update(self):
        project = ProjectFactory.create()
        client = APIClient()
        token = self._create_user()
        response = client.put(reverse('project-detail', kwargs={'pk': project.id}), {'name': 'Untitled-1'},
                              HTTP_AUTHORIZATION='Token ' + token)
        self.assertTrue(response.status_code == 403)


class RegisterViewTests(TestCase):
    def _create_user(self):
        response = self.client.post(
            reverse('auth_register'),
            {
                'username': 'chris',
                'email': 'chris@example.com',
                'password': 'SecretPassword!',
                'password_confirmation': 'SecretPassword!'
            },
        )
        return response.json()['token']

    def test_crud_projects(self):
        # First create the user
        token = self._create_user()
        client = APIClient()

        def project_count():
            r = client.get(reverse('project-list'), HTTP_AUTHORIZATION='Token ' + token)
            return r.json()['count']

        self.assertTrue(project_count() == 0)

        response = client.post(reverse('project-list'), {'name': 'Untitled'}, HTTP_AUTHORIZATION='Token ' + token)
        self.assertTrue(response.json()['name'] == 'Untitled')
        uuid = response.json()['id']

        response = client.get(reverse('project-detail', kwargs={'pk': uuid}), HTTP_AUTHORIZATION='Token ' + token)
        self.assertTrue(response.json()['id'] == uuid)
        self.assertTrue(response.json()['name'] == 'Untitled')

        self.assertTrue(project_count() == 1)

        response = client.put(reverse('project-detail', kwargs={'pk': uuid}), {'name': 'Untitled-1'},
                              HTTP_AUTHORIZATION='Token ' + token)
        self.assertTrue(response.json()['name'] == 'Untitled-1')

        client.delete(reverse('project-detail', kwargs={'pk': uuid}), {}, HTTP_AUTHORIZATION='Token ' + token)
        self.assertTrue(project_count() == 0)

    def test_crud_groups(self):
        # First create the user
        token = self._create_user()
        client = APIClient()
        # Create project
        project_1 = client.post(reverse('project-list'), {'name': 'Untitled'}, HTTP_AUTHORIZATION='Token ' + token).json()['id']
        project_2 = client.post(reverse('project-list'), {'name': 'Untitled-2'}, HTTP_AUTHORIZATION='Token ' + token).json()['id']
        response = client.post(
            reverse('group-list'),
            {'name': 'Group', 'project': project_1},
            HTTP_AUTHORIZATION='Token ' + token,
        )
        self.assertTrue(response.json()['name'] == 'Group')
        uuid = response.json()['id']

        response = client.put(
            reverse('group-detail', kwargs={'pk': uuid}),
            {'name': 'Untitled-1', 'project': project_2},
            HTTP_AUTHORIZATION='Token ' + token,
        )
        self.assertTrue(response.json()['project'] == project_2)

    def test_crud_layers(self):
        # First create the user
        token = self._create_user()
        client = APIClient()
        # Create project
        project = client.post(reverse('project-list'), {'name': 'Untitled'}, HTTP_AUTHORIZATION='Token ' + token).json()['id']
        group = client.post(
            reverse('group-list'),
            {'name': 'Group', 'project': project},
            HTTP_AUTHORIZATION='Token ' + token,
        ).json()['id']

        response = client.post(
            reverse('layer-list'),
            {'name': 'Layer 1', 'group': group, 'order': 1, 'rarity': 1},
            HTTP_AUTHORIZATION='Token ' + token,
        )
        self.assertTrue(response.json()['name'] == 'Layer 1')
        uuid = response.json()['id']
        response = client.put(
            reverse('layer-detail', kwargs={'pk': uuid}),
            {'name': 'Layer 2'},
            HTTP_AUTHORIZATION='Token ' + token,
        )

    def test_crud_assets(self):
        # First create the user
        token = self._create_user()
        client = APIClient()
        # Create project
        project = client.post(reverse('project-list'), {'name': 'Untitled'}, HTTP_AUTHORIZATION='Token ' + token).json()['id']
        group = client.post(
            reverse('group-list'),
            {'name': 'Group', 'project': project},
            HTTP_AUTHORIZATION='Token ' + token,
        ).json()['id']

        layer = client.post(
            reverse('layer-list'),
            {'name': 'Layer 1', 'group': group, 'order': 1, 'rarity': 1},
            HTTP_AUTHORIZATION='Token ' + token,
        ).json()['id']

        # Create asset
        response = client.post(
            reverse('asset-list'),
            {'name': 'Asset 1', 'layer': layer, 'rarity': 1},
            HTTP_AUTHORIZATION='Token ' + token,
        )
