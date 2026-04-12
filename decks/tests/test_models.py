import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from decks.models import Deck

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        username="model_test_user",
        password="secret123",
    )


def test_deck_has_owner(user):
    deck = Deck.objects.create(name="Python Basics", owner=user)

    assert deck.owner == user


def test_deck_name_is_unique_per_owner(user):
    Deck.objects.create(name="My Deck", owner=user)

    with pytest.raises(IntegrityError):
        Deck.objects.create(name="My Deck", owner=user)
