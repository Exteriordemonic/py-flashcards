from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from decks.models import Deck

User = get_user_model()


class DeckModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="model_test_user",
            password="secret123",
        )

    def test_deck_has_owner(self):
        deck = Deck.objects.create(name="Python Basics", owner=self.user)

        self.assertEqual(deck.owner, self.user)

    def test_deck_name_is_unique_per_owner(self):
        Deck.objects.create(name="My Deck", owner=self.user)

        with self.assertRaises(IntegrityError):
            Deck.objects.create(name="My Deck", owner=self.user)
