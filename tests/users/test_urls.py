import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse


@pytest.mark.django_db
def test_register_url(client):
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_url(client):
    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_url(client, register_user, login_user):
    login_user(client, register_user.username, 'Test@123')
    url = reverse('logout')
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_change_password_url(client, register_user, login_user):
    login_user(client, register_user.username, 'Test@123')
    url = reverse('change_password')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_url(client):
    url = reverse('password_reset')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_done_url(client):
    url = reverse('password_reset_done')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_confirm_url(client, register_user):
    token = default_token_generator.make_token(register_user)
    url = reverse('password_reset_confirm', kwargs={'uidb64': 'Mg', 'token': token})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_complete_url(client):
    url = reverse('password_reset_complete')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_url(client, register_admin, login_user, register_user):
    login_user(client, register_admin.username, 'Test@123')
    url = reverse('profile', kwargs={'username': register_admin.username})

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_update_url(client, register_user, login_user):
    login_user(client, 'chitrangda', 'Test@123')
    url = reverse('profile_update', kwargs={'pk': register_user.id})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_profile_url(client, register_user, login_user):
    login_user(client, register_user.username, 'Test@123')
    url = reverse('delete_profile')
    response = client.get(url)
    assert response.status_code == 302
