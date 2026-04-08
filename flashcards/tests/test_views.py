from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from flashcards.models import Deck, Flashcard

User = get_user_model()


class FlashcardAndDeckViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="view_user",
            password="secret123",
        )
        self.client.login(username="view_user", password="secret123")

        self.flashcard = Flashcard.objects.create(
            question="2 + 2 = ?",
            answer_a="3",
            answer_b="4",
            answer_c="5",
            answer_d="6",
            correct_answer="4",
            created_by=self.user,
        )
        self.deck = Deck.objects.create(name="Math", owner=self.user)

    def test_flashcard_list_view_for_logged_user(self):
        response = self.client.get(reverse("flashcards:flashcard-list"))
        self.assertEqual(response.status_code, 200)

    def test_flashcard_list_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("flashcards:flashcard-list"))
        self.assertEqual(response.status_code, 302)

    def test_flashcard_create_view_creates_object(self):
        response = self.client.post(
            reverse("flashcards:flashcard-create"),
            data={
                "question": "Capital of France?",
                "answer_a": "Berlin",
                "answer_b": "Madrid",
                "answer_c": "Paris",
                "answer_d": "Rome",
                "correct_answer": "Paris",
                "created_by": self.user.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Flashcard.objects.filter(question="Capital of France?").exists()
        )

    def test_flashcard_delete_view_deletes_object(self):
        response = self.client.post(
            reverse(
                "flashcards:flashcard-delete",
                kwargs={"pk": self.flashcard.id},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Flashcard.objects.filter(id=self.flashcard.id).exists()
        )

    def test_deck_create_view_creates_object(self):
        response = self.client.post(
            reverse("flashcards:deck-create"),
            data={
                "name": "Geography",
                "owner": self.user.id,
                "members": [self.user.id],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Deck.objects.filter(name="Geography").exists())

    def test_deck_delete_view_deletes_object(self):
        response = self.client.post(
            reverse("flashcards:deck-delete", kwargs={"pk": self.deck.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Deck.objects.filter(id=self.deck.id).exists())
