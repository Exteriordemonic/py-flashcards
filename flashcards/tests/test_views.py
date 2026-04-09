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


class FlashcardReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="view_user",
            password="secret123",
        )

        self.client.login(username="view_user", password="secret123")

        self.flashcard = Flashcard.objects.create(
            question="Capital of Poland?",
            answer_a="Warsaw",
            answer_b="Berlin",
            answer_c="Krakow",
            answer_d="Prague",
            correct_answer="Warsaw",
            deck=Deck.objects.create(name="Geography", owner=self.user),
            created_by=self.user,
        )

    def test_review_view_displays_question_and_options(self):
        url = reverse(
            "flashcards:flashcard-review", kwargs={"pk": self.flashcard.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Check question and all answers are shown
        self.assertIn("Capital of Poland?", content)
        self.assertIn("Warsaw", content)
        self.assertIn("Berlin", content)
        self.assertIn("Krakow", content)
        self.assertIn("Prague", content)

    def test_review_view_allows_answer_submission_and_feedback(self):
        url = reverse(
            "flashcards:flashcard-review", kwargs={"pk": self.flashcard.id}
        )

        # Simulate posting a correct answer
        response = self.client.post(url, {"selected_answer": "Warsaw"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(
            "correct", content.lower()
        )  # Should mention it's correct

        # Simulate posting an incorrect answer
        response = self.client.post(url, {"selected_answer": "Berlin"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(
            "incorrect", content.lower()
        )  # Should mention it's incorrect
