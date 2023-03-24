from unittest import TestCase

import pytest

from users.models import CustomUser


@pytest.mark.django_db
def test_post_creation(register_user2):
    assert isinstance(register_user2, CustomUser)
    assert register_user2.username == 'chitra'
    assert register_user2.email == 'test2@gmail.com'


