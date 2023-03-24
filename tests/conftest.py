import pytest
from django.contrib.auth.hashers import make_password

from content.models import ContentCategory, Content, Rewards, Likes, Comments
from users.models import CustomUser


@pytest.fixture()
def register_user():
    user = CustomUser.objects.create(email='test@gmail.com',
                                     first_name='chitrangda',
                                     last_name="pandya",
                                     password=make_password('Test@123', hasher='default'),
                                     username='chitrangda',
                                     wallet_address="0x5b78527fadb775e747a4d4a22f01d5a6a2cbd25e")
    return user


@pytest.fixture()
def register_user2():
    user = CustomUser.objects.create(email='test2@gmail.com',
                                     first_name='chitra',
                                     last_name="pandya",
                                     password=make_password('Test@123', hasher='default'),
                                     username='chitra')
    return user


@pytest.fixture
def login_user(db):
    def do_login(client, username, password):
        client.login(username=username, password=password)
        return client

    return do_login


@pytest.fixture
def register_admin():
    return CustomUser.objects.create(
        email='admin@gmail.com',
        first_name='admin',
        last_name='admin',
        password=make_password('Test@123', hasher='default'),
        username='admin123',
        is_superuser=True,
    )


@pytest.fixture()
def content_category():
    return ContentCategory.objects.create(category='lifestyle')


@pytest.fixture()
def rewards_fixture():
    return Rewards.objects.create(
        token=2, target=200, target_type='like', reward_badge="hbjhbjhb"
    )


@pytest.fixture()
def content_fixture(register_user, content_category):
    return Content.objects.create(
        user_id=register_user.id,
        ipfs_address='QmQudrmAfutTMCtJ7sEqDG4jgncdgAuJSWW1psUb5Ve7yn',
        category=content_category,
    )


@pytest.fixture()
def like_fixture(content_fixture, register_user):
    return Likes.objects.create(
        content_id=content_fixture.id, user_id=register_user.id
    )


@pytest.fixture()
def comment_fixture(content_fixture, register_user):
    return Comments.objects.create(
        content_id=content_fixture.id, user_id=register_user.id, comment="good"
    )


@pytest.fixture()
def make_archive_content(content_fixture, register_user):
    content_fixture.is_archived = True
    content_fixture.save()
    return content_fixture
