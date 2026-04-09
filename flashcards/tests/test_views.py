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
            deck=Deck.objects.create(name="Math", owner=self.user),
            created_by=self.user,
        )
        self.deck = self.flashcard.deck

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
                "correct_answer": "C",
                "deck": self.deck.id,
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
            deck=Deck.objects.create(name="User2 Deck", owner=self.user2),
            created_by=self.user2,
        )
        response = self.client.get(reverse("flashcards:flashcard-list"))

        self.assertEqual(response.status_code, 200)
        # Should contain current user's flashcard
        self.assertContains(response, self.flashcard.question)
        # Should not contain flashcard of the other user
        self.assertNotContains(response, "Question owned by user2")

    def test_flashcard_list_show_correct_data_for_decks(self):
        Flashcard.objects.create(
            question="Question owned by user2",
            answer_a="A",
            answer_b="B",
            answer_c="C",
            answer_d="D",
            correct_answer="A",
            deck=self.deck,
            created_by=self.user,
        )

        response = self.client.get(reverse("flashcards:flashcard-list"))
        self.assertEqual(response.status_code, 200)
        # Should contains the deck name
        self.assertContains(response, self.deck.name)

    def test_deck_detail_view_that_is_not_owner(self):
        self.client.login(username="view_user2", password="secret123")

        response = self.client.get(
            reverse("flashcards:deck-detail", kwargs={"pk": self.deck.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_deck_show_only_owner_flashcards_on_deck(self):
        Flashcard.objects.create(
            question="Question for user 2",
            answer_a="A",
            answer_b="B",
            answer_c="C",
            answer_d="D",
            correct_answer="A",
            deck=self.deck,
            created_by=self.user2,
        )

        response = self.client.get(
            reverse("flashcards:deck-detail", kwargs={"pk": self.deck.id})
        )
        # Ensure user is owner to view flashcards in deck;
        # user2 flashcard should NOT appear
        self.assertEqual(response.status_code, 200)
        response_content = response.content.decode()
        self.assertNotIn("Question for user 2", response_content)

    def test_create_flashcard_in_deck(self):
        initial_count = Flashcard.objects.count()
        response = self.client.post(
            reverse("flashcards:deck-detail", kwargs={"pk": self.deck.id}),
            data={
                "question": "What is the capital of Italy?",
                "answer_a": "Paris",
                "answer_b": "Rome",
                "answer_c": "Berlin",
                "answer_d": "Madrid",
                "correct_answer": "B",
            },
        )

        self.assertIn(response.status_code, [200])
        self.assertEqual(Flashcard.objects.count(), initial_count + 1)
        flashcard = Flashcard.objects.get(
            question="What is the capital of Italy?"
        )
        self.assertEqual(flashcard.deck, self.deck)
        self.assertEqual(flashcard.created_by, self.user)
        self.assertEqual(flashcard.correct_answer, "Rome")

    def test_create_flashcard_in_deck_ignores_posted_deck_and_uses_url_deck(
        self,
    ):
        another_deck = Deck.objects.create(
            name="Another deck", owner=self.user
        )
        self.client.post(
            reverse("flashcards:deck-detail", kwargs={"pk": self.deck.id}),
            data={
                "question": "Deck should come from URL",
                "answer_a": "A1",
                "answer_b": "B1",
                "answer_c": "C1",
                "answer_d": "D1",
                "correct_answer": "A",
                "deck": another_deck.id,
            },
        )
        flashcard = Flashcard.objects.get(question="Deck should come from URL")
        self.assertEqual(flashcard.deck, self.deck)  # deck z URL, nie z POSTa

    def test_create_flashcard_in_deck_requires_owner(self):
        self.client.logout()
        self.client.login(username="view_user2", password="secret123")
        initial_count = Flashcard.objects.count()
        response = self.client.post(
            reverse("flashcards:deck-detail", kwargs={"pk": self.deck.id}),
            data={
                "question": "Unauthorized add attempt",
                "answer_a": "A",
                "answer_b": "B",
                "answer_c": "C",
                "answer_d": "D",
                "correct_answer": "A",
            },
        )
        self.assertEqual(
            response.status_code, 404
        )  # OwnerQuerysetMixin should cut off unauthorized users

        self.assertEqual(Flashcard.objects.count(), initial_count)

    def test_create_flashcard_in_deck_invalid_data_does_not_create(self):
        initial_count = Flashcard.objects.count()
        response = self.client.post(
            reverse("flashcards:deck-detail", kwargs={"pk": self.deck.id}),
            data={
                "question": "",  # invalid: required
                "answer_a": "A",
                "answer_b": "B",
                "answer_c": "C",
                "answer_d": "D",
                "correct_answer": "A",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Flashcard.objects.count(), initial_count)
