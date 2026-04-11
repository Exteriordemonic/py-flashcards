from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from decks.models import Deck
from flashcards.models import Flashcard, FlashcardUserState, Answer

User = get_user_model()


class SetupTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="flashcard_owner",
            password="secret123",
        )

        self.client.login(
            username="flashcard_owner",
            password="secret123",
        )

        self.deck = Deck.objects.create(name="Owner Deck", owner=self.user)

        self.flashcard = Flashcard.objects.create(
            question="What is capitol of Poland?",
            deck=self.deck,
            created_by=self.user,
        )

        self.a1 = Answer.objects.create(
            text="Warsaw", is_correct=True, flashcard=self.flashcard
        )
        self.a2 = Answer.objects.create(text="Paris", flashcard=self.flashcard)
        self.a2 = Answer.objects.create(
            text="Berlin", flashcard=self.flashcard
        )


class FlashcardModelTests(SetupTest):
    def test_created_by_is_set_null_when_user_deleted(self):

        self.user.delete()
        self.flashcard.refresh_from_db()

        self.assertIsNone(self.flashcard.created_by)


class FlashcardUserStateModelTests(TestCase):
    def test_flashcard_user_state_is_unique_for_flashcard_and_user(self):

        FlashcardUserState.objects.create(
            flashcard=self.flashcard,
            user=self.user,
            next_review_at="2026-04-09",
        )

        with self.assertRaises(IntegrityError):
            FlashcardUserState.objects.create(
                flashcard=self.flashcard,
                user=self.user,
                next_review_at="2026-04-10",
            )
