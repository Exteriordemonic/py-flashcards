from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from decks.models import Deck
from flashcards.models import Flashcard, FlashcardUserState

User = get_user_model()


class FlashcardModelTests(TestCase):
    def test_created_by_is_set_null_when_user_deleted(self):
        user = User.objects.create_user(
            username="flashcard_owner",
            password="secret123",
        )
        deck_owner = User.objects.create_user(
            username="deck_owner",
            password="secret123",
        )
        deck = Deck.objects.create(name="Owner Deck", owner=deck_owner)
        flashcard = Flashcard.objects.create(
            question="What is 2 + 2?",
            answer_a="3",
            answer_b="4",
            answer_c="5",
            answer_d="6",
            correct_answer="4",
            deck=deck,
            created_by=user,
        )

        user.delete()
        flashcard.refresh_from_db()

        self.assertIsNone(flashcard.created_by)


class FlashcardUserStateModelTests(TestCase):
    def test_flashcard_user_state_is_unique_for_flashcard_and_user(self):
        user = User.objects.create_user(
            username="state_user",
            password="secret123",
        )
        flashcard = Flashcard.objects.create(
            question="Capital of Poland?",
            answer_a="Krakow",
            answer_b="Warsaw",
            answer_c="Gdansk",
            answer_d="Wroclaw",
            correct_answer="Warsaw",
            deck=Deck.objects.create(name="State Deck", owner=user),
            created_by=user,
        )

        FlashcardUserState.objects.create(
            flashcard=flashcard,
            user=user,
            next_review_at="2026-04-09",
        )

        with self.assertRaises(IntegrityError):
            FlashcardUserState.objects.create(
                flashcard=flashcard,
                user=user,
                next_review_at="2026-04-10",
            )
