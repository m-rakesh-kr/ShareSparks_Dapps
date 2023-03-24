import pytest


@pytest.mark.django_db
def test_registration_sucess(client):
    register_data = {
        'email': 'chitra1562001@gmail.com',
        'first_name': 'chitrangda',
        'last_name': "pandya",
        'password1': 'Test@123',
        'password2': 'Test@123',
        'username': 'chitra'
    }
    response = client.post("/register/", data=register_data)
    assert response.status_code == 302
    assert response.url == '/login/'


@pytest.mark.django_db
def test_registration_pass2_doesnot_match(client):
    register_data = {
        'email': 'chitra1562001@gmail.com',
        'first_name': 'chitrangda',
        'last_name': "pandya",
        'password1': 'Test@123',
        'password2': 'Tes@123',
        'username': 'chitra'
    }
    response = client.post("/register/", data=register_data)
    assert b"The two password fields didn\xe2\x80\x99t match." in response.content


@pytest.mark.django_db
def test_registration_username_error(client, register_user):
    register_data = {
        'email': 'chitra1562001@gmail.com',
        'first_name': 'chitrangda',
        'last_name': "pandya",
        'password1': 'Test@123',
        'password2': 'Test@123',
        'username': 'chitrangda'
    }
    response = client.post("/register/", data=register_data)
    assert b" A user with that username already exists." in response.content


@pytest.mark.django_db
def test_registration_password_too_short(client, register_user):
    register_data = {
        'email': 'chitra1562001@gmail.com',
        'first_name': 'chitrangda',
        'last_name': "pandya",
        'password1': 'Test@1',
        'password2': 'Test@1',
        'username': 'chitrangda'
    }
    response = client.post("/register/", data=register_data)
    assert b"This password is too short. It must contain at least 8 characters" in response.content


@pytest.mark.django_db
def test_registration_email_error(client, register_user):
    register_data = {
        'email': 'test@gmail.com',
        'first_name': 'chitrangda',
        'last_name': "pandya",
        'password1': 'Test@123',
        'password2': 'Test@123',
        'username': 'chitrangda'
    }
    response = client.post("/register/", data=register_data)
    assert b"User with this Email already exists." in response.content


@pytest.mark.django_db
def test_login_success(client, register_user):
    login_data = {
        'username': 'chitrangda',
        'password': 'Test@123'
    }
    response = client.post('/login/', data=login_data)
    assert response.status_code == 302
    assert response.url == '/'


@pytest.mark.django_db
def test_login_incorrect_password(client, register_user):
    login_data = {
        'username': 'chitrangda',
        'password': 'Test@23'
    }
    response = client.post('/login/', data=login_data)
    assert b"Invalid login credentials" in response.content


@pytest.mark.django_db
def test_login_username_error(client, register_user):
    login_data = {
        'username': 'chitragda',
        'password': 'Test@123'
    }
    response = client.post('/login/', data=login_data)
    assert b"Invalid login credentials" in response.content


@pytest.mark.django_db
def test_login_success(client, register_user):
    login_data = {
        'username': 'chitrangda',
        'password': 'Test@123'
    }
    response = client.post('/login/', data=login_data)
    assert response.status_code == 302
    assert response.url == '/'


@pytest.mark.django_db
def test_change_password_sucess(client, register_user, login_user):
    login_user(client, 'chitrangda', 'Test@123')
    register_data = {
        'old_password': 'Test@123',
        'new_password1': 'ABC@12345',
        'new_password2': 'ABC@12345'
    }
    response = client.post("/change-password/", data=register_data)
    return response.status_code == 200


@pytest.mark.django_db
def test_change_password_sucess(client, register_user, login_user):
    login_user(client, 'chitrangda', 'Test@123')
    register_data = {
        'old_password': 'Tes@123',
        'new_password1': 'ABC@12345',
        'new_password2': 'ABC@12345'
    }
    response = client.post("/change-password/", data=register_data)
    return B"Your old password was entered incorrectly. Please enter it again." in response.content


@pytest.mark.django_db
def test_profile_success(client, register_admin, login_user):
    login_user(client, register_admin.username, 'Test@123')
    response = client.get(f"/profile/{register_admin.username}/")
    assert response.status_code == 200
    # assert response.template.name == 'profile.html'


@pytest.mark.django_db
def test_profile_failure(client, register_user, login_user):
    login_user(client, 'chitrangda', 'Test@123')
    response = client.get("/profile/chrangda/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_profile_get_update_success(client, register_user, login_user):
    login_user(client, 'chitrangda', 'Test@123')
    data = {
        'username': 'chitra'
    }
    response = client.get(f"/profile/{register_user.id}/update/", data=data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_update_success(client, register_user, login_user):
    login_user(client, 'chitrangda', 'Test@123')
    data = {
        'email': 'chitra@gmail.com',
        'username': 'username'
    }
    response = client.post(f"/profile/{register_user.id}/update/", data=data)
    assert response.status_code == 302
    assert response.url == "/profile/username/"


@pytest.mark.django_db
def test_profile_update_failure_username_already_exists(client, register_user, register_user2, login_user):
    login_user(client, 'chitrangda', 'Test@123')
    data = {
        'email': 'test2@gmail.com',
        'username': 'chitra'
    }
    response = client.post(f"/profile/{register_user.id}/update/", data=data)
    assert b"A user with that username already exists" in response.content


@pytest.mark.django_db
def test_profile_update_failure_email_already_exists(client, register_user, register_user2, login_user):
    login_user(client, 'chitrangda', 'Test@123')
    data = {
        'email': 'test2@gmail.com',
        'username': 'chitraspam'
    }
    response = client.post(f"/profile/{register_user.id}/update/", data=data)
    assert b"User with this Email already exists." in response.content


@pytest.mark.django_db
def test_password_reset_mail_success(client, register_user):
    data = {
        'email': 'test@gmail.com'
    }
    response = client.post("/password-reset/", data=data)
    assert response.status_code == 302
    assert response.url == '/password-reset/done/'


@pytest.mark.django_db
def test_password_reset_failure(client):
    data = {
        'email': 'tgg21424@gmail.com'
    }
    response = client.post("/password-reset/", data=data)
    # breakpoint()
    assert response.status_code == 405
    print(response)