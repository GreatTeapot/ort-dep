import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


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
    assert 'access_token' in response.data