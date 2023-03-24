import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_url(client, register_user, login_user):
    login_user(client, username=register_user.username, password="Test@123")
    url = reverse('home')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_category(client, register_admin, login_user):
    login_user(client, username="admin123", password="Test@123")
    url = reverse('add_category')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_categories(client, register_admin, login_user):
    login_user(client, username="admin123", password="Test@123")
    url = reverse('view_categories')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_category(client, register_admin, login_user, content_category):
    login_user(client, username="admin123", password="Test@123")
    url = reverse('update_category', kwargs={'pk': content_category.id})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_category(client, register_admin, login_user, content_category):
    login_user(client, username="admin123", password="Test@123")
    url = reverse('delete_category', kwargs={'pk': content_category.id})
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_add_reward(client, register_admin, login_user):
    login_user(client, username="admin123", password="Test@123")
    url = reverse('add_reward')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_rewards(client, register_admin, login_user):
    login_user(client, username="admin123", password="Test@123")
    url = reverse('view_rewards')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_reward(client, register_admin, login_user, rewards_fixture):
    login_user(client, username="admin123", password="Test@123")
    url = reverse('update_reward', kwargs={'pk': rewards_fixture.id})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_reward(client, register_admin, login_user, rewards_fixture):
    login_user(client, username="admin123", password="Test@123")
    url = reverse('delete_reward', kwargs={'pk': rewards_fixture.id})
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_like(client, register_admin, login_user, content_fixture):
    login_user(client, username="admin123", password="Test@123")
    url = reverse('like', kwargs={'content_id': content_fixture.id})
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_unlike(client, register_user, login_user, content_fixture, like_fixture):
    login_user(client, username="chitrangda", password="Test@123")
    url = reverse('unlike', kwargs={'content_id': like_fixture.content_id})
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_comment(client, register_user, login_user, content_fixture, comment_fixture):
    login_user(client, username="chitrangda", password="Test@123")
    url = reverse('delete_comment', kwargs={'pk': comment_fixture.id})
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_view_comments(client, register_user, login_user, content_fixture, comment_fixture):
    login_user(client, username="chitrangda", password="Test@123")
    url = reverse('view_comments', kwargs={'content_id': content_fixture.id})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_archive(client, register_user, login_user, content_fixture, comment_fixture):
    login_user(client, username="chitrangda", password="Test@123")
    url = reverse('archive_content', kwargs={'content_id': content_fixture.id})
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_view_archive_content(client, register_user2, login_user, make_archive_content):
    login_user(client, username=register_user2.username, password="Test@123")

    url = reverse('view_archive_content')
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_view_detailed_archive_content(client, register_user2, login_user, make_archive_content):
    login_user(client, username=register_user2.username, password="Test@123")
    url = reverse('view_detailed_archived_content', kwargs={'content_id': make_archive_content.id})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_content_rewards(client, register_user2, login_user, content_fixture):
    login_user(client, username=register_user2.username, password="Test@123")
    url = reverse('content_rewards', kwargs={'content_id': content_fixture.id})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_content_rewards(client, register_admin, login_user, content_fixture):
    login_user(client, username=register_admin.username, password="Test@123")
    url = reverse('content_rewards', kwargs={'content_id': content_fixture.id})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_filter_posts(client, register_user, login_user, content_fixture, content_category):
    login_user(client, username=register_user.username, password="Test@123")
    url = reverse('filter-content', kwargs={'category': content_category.category})
    response = client.get(url)
    assert response.status_code == 200
