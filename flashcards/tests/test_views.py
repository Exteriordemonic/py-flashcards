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

        self.user2 = User.objects.create_user(
            username="view_user2",
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

    def test_flashcard_list_show_current_user_flashcardsdef(self):
        # Test that flashcard list view only shows flashcards created by current user
        Flashcard.objects.create(
            question="Question owned by user2",
            answer_a="A",
            answer_b="B",
            answer_c="C",
            answer_d="D",
            correct_answer="A",
            created_by=self.user2,
        )
        response = self.client.get(reverse("flashcards:flashcard-list"))

        self.assertEqual(response.status_code, 200)
        # Should contain current user's flashcard
        self.assertContains(response, self.flashcard.question)
        # Should not contain flashcard of the other user
        self.assertNotContains(response, "Question owned by user2")

    def test_flashcard_list_show_correct_data_for_decks(self):
        flashcard = Flashcard.objects.create(
            question="Question owned by user2",
            answer_a="A",
            answer_b="B",
            answer_c="C",
            answer_d="D",
            correct_answer="A",
            created_by=self.user,
        )

        flashcard.deck.set([self.deck])

        response = self.client.get(reverse("flashcards:flashcard-list"))
        self.assertEqual(response.status_code, 200)
        # Should contains the deck name
        self.assertContains(response, self.deck.name)
