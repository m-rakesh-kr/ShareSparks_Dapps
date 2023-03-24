from unittest import TestCase

import pytest

from content.models import ContentCategory, Rewards, Content, Likes, Comments, ContentVersion, ContentRewards


@pytest.mark.django_db
class CategoryModelTestCase(TestCase):

    def test_my_model_creation(self):
        my_model = ContentCategory.objects.create(category='category')
        self.assertIsInstance(my_model, ContentCategory)
        self.assertEqual(my_model.category, 'CATEGORY')

    def test_my_model_update(self):
        my_model = ContentCategory.objects.create(category='test')
        my_model.category = 'updated name'
        my_model.save()
        updated_model = ContentCategory.objects.get(id=my_model.id)
        self.assertEqual(updated_model.category, 'UPDATED NAME')

    def test_my_model_deletion(self):
        my_model = ContentCategory.objects.create(category='test')
        my_model.delete()
        with self.assertRaises(ContentCategory.DoesNotExist):
            ContentCategory.objects.get(category='test')


@pytest.mark.django_db
class RewardsModelTestCase(TestCase):

    def test_my_model_creation(self):
        my_model = Rewards.objects.create(token=2, target=200, target_type='like')
        self.assertIsInstance(my_model, Rewards)
        self.assertEqual(my_model.token, 2)
        self.assertEqual(my_model.target, 200)
        self.assertEqual(my_model.target_type, 'like')

    def test_my_model_update(self):
        my_model = Rewards.objects.create(token=2, target=200, target_type='like')
        my_model.token = 9
        my_model.save()
        updated_model = Rewards.objects.get(id=my_model.id)
        self.assertEqual(updated_model.token, 9)

    def test_my_model_deletion(self):
        my_model = Rewards.objects.create(token=2, target=200, target_type='like')
        my_model.delete()
        with self.assertRaises(Rewards.DoesNotExist):
            Rewards.objects.get(token=2)


@pytest.mark.django_db
def test_my_model_creation(client, register_admin, login_user, content_category):
    login_user(client, 'chitrangda', 'Test@123')
    my_model = Content.objects.create(user_id=1,
                                      ipfs_address='QmQudrmAfutTMCtJ7sEqDG4jgncdgAuJSWW1psUb5Ve7yn', category_id=content_category.id)
    assert isinstance(my_model, Content)
    assert my_model.ipfs_address == "QmQudrmAfutTMCtJ7sEqDG4jgncdgAuJSWW1psUb5Ve7yn"


@pytest.mark.django_db
def test_my_model_update(client, register_admin, login_user, content_category):
    login_user(client, 'chitrangda', 'Test@123')

    my_model = Content.objects.create(user_id=register_admin.id,
                                      ipfs_address='QmQudrmAfutTMCtJ7sEqDG4jgncdgAuJSWW1psUb5Ve7yn',category=content_category)
    my_model.ipfs_address = "hello"
    my_model.save()
    updated_model = Content.objects.get(id=my_model.id)
    assert updated_model.ipfs_address == "hello"


@pytest.mark.django_db
def test_like_model_creation(client, register_user, login_user, content_fixture):
    like_model = Likes.objects.create(content_id=content_fixture.id, user_id=register_user.id)
    assert isinstance(like_model, Likes)
    assert like_model.content == content_fixture
    assert like_model.user == register_user


@pytest.mark.django_db
def test_like_model_update(client, register_user, register_user2, login_user, content_fixture):
    like_model = Likes.objects.create(content_id=content_fixture.id, user_id=register_user.id)
    like_model.user_id = register_user2.id
    like_model.save()
    updated_model = Likes.objects.get(user_id=register_user2.id)
    assert updated_model.user_id == register_user2.id


@pytest.mark.django_db
def test_comment_model_creation(client, register_user, login_user, content_fixture):
    comment_model = Comments.objects.create(content_id=content_fixture.id, user_id=register_user.id
                                            , comment="Very Nice")
    assert comment_model.comment == "Very Nice"
    assert comment_model.user == register_user


@pytest.mark.django_db
def test_comment_model_update(client, register_user, register_user2, login_user, content_fixture):
    comment_model = Comments.objects.create(content_id=content_fixture.id, user_id=register_user.id, comment="hello")
    comment_model.comment = "hi"
    comment_model.save()
    updated_model = Comments.objects.get(comment="hi")
    assert updated_model.comment == "hi"


@pytest.mark.django_db
def test_content_version_creation(client, content_fixture):
    version_model = ContentVersion.objects.create(ipfs_address="vsuyc", version_number=2, content_id=content_fixture.id)
    assert isinstance(version_model, ContentVersion)
    assert version_model.version_number == 2
    assert version_model.ipfs_address == "vsuyc"


@pytest.mark.django_db
def test_version_updation(client, content_fixture):
    version_model = ContentVersion.objects.create(ipfs_address="vsuyc", version_number=2, content_id=content_fixture.id)
    version_model.ipfs_address = "ipfs"
    version_model.save()
    updated_model = ContentVersion.objects.get(ipfs_address="ipfs")
    assert updated_model.ipfs_address == "ipfs"


@pytest.mark.django_db
def test_content_rewards(client, content_fixture, rewards_fixture):
    content_reward_model = ContentRewards.objects.create(content_id=content_fixture.id, reward_id=rewards_fixture.id,
                                                         transaction_link="snkjnjskn"
                                                         )
    assert isinstance(content_reward_model, ContentRewards)
    assert content_reward_model.content == content_fixture
