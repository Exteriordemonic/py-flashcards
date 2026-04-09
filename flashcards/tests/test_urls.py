from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from flashcards.models import Deck, Flashcard


User = get_user_model()


class TestUrls(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword2"
        )

        self.client.login(username="testuser", password="testpassword")

    def create_flashcard(self):
        deck = self.create_deck()
        return Flashcard.objects.create(
            question="Jaka jest stolica Polski?",
            answer_a="Gdańsk",
            answer_b="Kraków",
            answer_c="Warszawa",
            answer_d="Wrocław",
            correct_answer="Warszawa",
            deck=deck,
            created_by=self.user,
        )

    def create_deck(self):
        return Deck.objects.create(name="Example Deck 1", owner=self.user)

    def test_flashcard_list_is_resolved(self):
        response = self.client.get(reverse("flashcards:flashcard-list"))
        self.assertEqual(response.status_code, 200)

    def test_flashcard_detail_is_resolved(self):
        flashcard = self.create_flashcard()

        response = self.client.get(
            reverse("flashcards:flashcard-detail", kwargs={"pk": flashcard.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_flashcard_create_is_resolved(self):
        response = self.client.get(reverse("flashcards:flashcard-create"))
        self.assertEqual(response.status_code, 200)

    def test_flashcard_update_is_resolved(self):
        flashcard = self.create_flashcard()

        response = self.client.get(
            reverse("flashcards:flashcard-update", kwargs={"pk": flashcard.id})
        )
        self.assertEqual(
            response.status_code,
            200,
        )

    def test_flashcard_delete_is_resolved(self):
        flashcard = self.create_flashcard()

        response = self.client.get(
            reverse("flashcards:flashcard-delete", kwargs={"pk": flashcard.id})
        )
        self.assertEqual(
            response.status_code,
            200,
        )

    def test_deck_list_is_resolved(self):
        response = self.client.get(reverse("flashcards:deck-list"))
        self.assertEqual(response.status_code, 200)

    def test_deck_detail_is_resolved(self):
        deck = self.create_deck()

        response = self.client.get(
            reverse("flashcards:deck-detail", kwargs={"pk": deck.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_deck_create_is_resolved(self):
        response = self.client.get(reverse("flashcards:deck-create"))
        self.assertEqual(response.status_code, 200)

    def test_deck_update_is_resolved(self):
        deck = self.create_deck()

        response = self.client.get(
            reverse("flashcards:deck-update", kwargs={"pk": deck.id})
        )
        self.assertEqual(
            response.status_code,
            200,
        )

    def test_deck_delete_is_resolved(self):
        deck = self.create_deck()

        response = self.client.get(
            reverse("flashcards:deck-delete", kwargs={"pk": deck.id})
        )
        self.assertEqual(
            response.status_code,
            200,
        )

    def test_not_logged_in_access(self):
        self.client.logout()
        flashcard = self.create_flashcard()
        deck = flashcard.deck
        urls = [
            reverse("flashcards:flashcard-list"),
            reverse("flashcards:flashcard-create"),
            reverse(
                "flashcards:flashcard-detail", kwargs={"pk": flashcard.id}
            ),
            reverse(
                "flashcards:flashcard-update", kwargs={"pk": flashcard.id}
            ),
            reverse(
                "flashcards:flashcard-delete", kwargs={"pk": flashcard.id}
            ),
            reverse("flashcards:deck-list"),
            reverse("flashcards:deck-create"),
            reverse("flashcards:deck-detail", kwargs={"pk": deck.id}),
            reverse("flashcards:deck-update", kwargs={"pk": deck.id}),
            reverse("flashcards:deck-delete", kwargs={"pk": deck.id}),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_redirect_if_user_have_no_access_to_the_deck(self):
        deck = self.create_deck()

        self.client.login(username="testuser2", password="testpassword2")
        response = self.client.get(
            reverse("flashcards:deck-detail", kwargs={"pk": deck.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_redirect_if_user_tries_to_delete_not_owned_deck(self):
        deck = self.create_deck()

        self.client.login(username="testuser2", password="testpassword2")
        response = self.client.get(
            reverse("flashcards:deck-delete", kwargs={"pk": deck.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_redirect_if_user_tries_to_update_not_owned_deck(self):
        deck = self.create_deck()

        self.client.login(username="testuser2", password="testpassword2")
        response = self.client.get(
            reverse("flashcards:deck-update", kwargs={"pk": deck.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_redirect_if_user_tries_to_view_not_owned_flashcard(self):
        flashcard = self.create_flashcard()

        self.client.login(username="testuser2", password="testpassword2")
        response = self.client.get(
            reverse("flashcards:flashcard-detail", kwargs={"pk": flashcard.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_redirect_if_user_tries_to_update_not_owned_flashcard(self):
        flashcard = self.create_flashcard()

        self.client.login(username="testuser2", password="testpassword2")
        response = self.client.get(
            reverse("flashcards:flashcard-update", kwargs={"pk": flashcard.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_redirect_if_user_tries_to_delete_not_owned_flashcard(self):
        flashcard = self.create_flashcard()

        self.client.login(username="testuser2", password="testpassword2")
        response = self.client.get(
            reverse("flashcards:flashcard-delete", kwargs={"pk": flashcard.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_review_flashcard(self):
        flashcard = self.create_flashcard()

        response = self.client.get(
            reverse("flashcards:flashcard-review", kwargs={"pk": flashcard.id})
        )

        self.assertEqual(response.status_code, 200)

    def test_review_flashcard_without_access_returns_404(self):
        flashcard = self.create_flashcard()

        self.client.login(username="testuser2", password="testpassword2")

        response = self.client.get(
            reverse("flashcards:flashcard-review", kwargs={"pk": flashcard.id})
        )

        self.assertEqual(response.status_code, 404)
