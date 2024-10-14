import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser


@pytest.mark.django_db
def test_registration():
    client = APIClient()
    url = reverse('register')
    data = {
        'username': 'testuser',
        'password': 'testpassword123',
        'email': 'testuser@example.com',
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in response.cookies


@pytest.mark.django_db
def test_user_profile():
    user = CustomUser.objects.create_user(
        username='testuser2', password='testpassword123', email='testuser2@example.com'
    )
    client = APIClient()
    client.login(username='testuser2', password='testpassword123')

    url = reverse('user-info')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'testuser2'
