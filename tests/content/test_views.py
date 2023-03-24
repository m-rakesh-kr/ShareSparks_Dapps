import pytest


@pytest.mark.django_db
def test_add_category_permission_denied(client, register_user, login_user, content_fixture):
    login_user(client, 'chitrangda', 'Test@123')
    data = {
        'category': 'travel'
    }
    response = client.post("/add-category/", data=data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_add_category_success(client, register_admin, login_user):
    login_user(client, register_admin.username, 'Test@123')
    data = {
        'category': 'travel'
    }
    response = client.post("/add-category/", data=data)
    assert response.status_code == 302


@pytest.mark.django_db
def test_add_category_view(client, register_admin, login_user):
    login_user(client, register_admin.username, 'Test@123')
    response = client.get("/add-category/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_list_categories(client, register_admin, login_user):
    login_user(client, register_admin.username, 'Test@123')
    response = client.get('/view-categories/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_categories(client, register_admin, login_user, content_category):
    login_user(client, register_admin.username, 'Test@123')
    response = client.post(f'/update-category/{content_category.id}')
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_category_failure(client, register_admin, login_user, content_category):
    login_user(client, register_admin.username, 'Test@123')
    response = client.post('/update-category/2')
    assert response.status_code == 404


@pytest.mark.django_db
def test_update_category_not_allowed(client, register_user, login_user, content_category):
    login_user(client, register_user.username, 'Test@123')
    response = client.post(f'/update-category/{content_category.id}')
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_categories(client, register_admin, login_user, content_category):
    login_user(client, register_admin.username, 'Test@123')
    response = client.get(f'/delete-category/{content_category.id}')
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_category_failure(client, register_admin, login_user, content_category):
    login_user(client, register_admin.username, 'Test@123')
    response = client.get('/delete-category/2')
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_category_not_allowed(client, register_user, login_user, content_category):
    login_user(client, register_user.username, 'Test@123')
    response = client.get(f'/delete-category/{content_category.id}')
    assert response.status_code == 403


@pytest.mark.django_db
def test_add_reward_permission_denied(client, register_user, login_user, content_fixture):
    login_user(client, 'chitrangda', 'Test@123')
    data = {
        'token': 25,
        'target': 400,
        'like_or_comment': 'like'
    }
    response = client.post("/add-reward/", data=data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_add_reward_success(client, register_admin, login_user):
    login_user(client, register_admin.username, 'Test@123')
    data = {
        'token': 25,
        'target': 400,
        'like_or_comment': 'like'
    }
    response = client.post("/add-reward/", data=data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_reward_view(client, register_admin, login_user):
    login_user(client, register_admin.username, 'Test@123')
    response = client.get("/add-reward/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_list_rewards(client, register_admin, login_user):
    login_user(client, register_admin.username, 'Test@123')
    response = client.get('/view-rewards/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_list_rewards_not_allowed(client, register_user, login_user):
    login_user(client, register_user.username, 'Test@123')
    response = client.get('/view-rewards/')
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_rewards_success(client, register_admin, login_user, rewards_fixture):
    login_user(client, register_admin.username, 'Test@123')
    response = client.post(f'/update-reward/{rewards_fixture.id}')
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_rewards_not_allowed(client, register_user, login_user, rewards_fixture):
    login_user(client, register_user.username, 'Test@123')
    response = client.post(f'/update-reward/{rewards_fixture.id}')
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_reward(client, register_admin, login_user, rewards_fixture):
    login_user(client, register_admin.username, 'Test@123')
    response = client.get(f'/delete-reward/{rewards_fixture.id}')
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_reward_failure(client, register_admin, login_user, rewards_fixture):
    login_user(client, register_admin.username, 'Test@123')
    response = client.get('/delete-reward/2')
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_reward_not_allowed(client, register_user, login_user, rewards_fixture):
    login_user(client, register_user.username, 'Test@123')
    response = client.get(f'/delete-reward/{rewards_fixture.id}')
    assert response.status_code == 403


@pytest.mark.django_db
def test_like_success(client, register_user, login_user, content_fixture):
    login_user(client, register_user.username, 'Test@123')
    response = client.get(f'/content/like/{content_fixture.id}')
    assert response.status_code == 302


@pytest.mark.django_db
def test_like_login_required(client, register_user, login_user, content_fixture):
    response = client.get(f'/content/like/{content_fixture.id}')
    assert response.status_code == 302


@pytest.mark.django_db
def test_unlike_success(client, register_user, login_user, content_fixture, like_fixture):
    login_user(client, register_user.username, 'Test@123')
    response = client.get(f'/content/unlike/{content_fixture.id}')
    assert response.status_code == 302


@pytest.mark.django_db
def test_view_comments(client, register_user, login_user, content_fixture):
    login_user(client, register_user.username, 'Test@123')
    response = client.get(f'/view-comments/{content_fixture.id}')
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_comments(client, register_user, login_user, content_fixture, comment_fixture):
    login_user(client, register_user.username, 'Test@123')
    response = client.get(f'/delete-comment/{comment_fixture.id}')
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_comments_not_allowed(client, register_user2, login_user, content_fixture, comment_fixture):
    login_user(client, register_user2.username, 'Test@123')
    response = client.get(f'/delete-comment/{comment_fixture.id}')
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_comments_login_required(client, register_user, login_user, content_fixture, comment_fixture):
    login_user(client, register_user.username, 'Test@123')
    response = client.get(f'/delete-comment/{comment_fixture.id}')
    assert response.status_code == 302


@pytest.mark.django_db
def test_home_view(client):
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_content_view(client, login_user, register_user, content_category):
    login_user(client, register_user.username, 'Test@123')
    data = {
        'title': 'Title',
        'data': 'DARTA DATA DATA',
        'category': content_category.id,

    }
    response = client.post('/add-content/', data=data)
    assert response.status_code == 200

