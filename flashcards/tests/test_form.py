from django.test import TestCase
from django.contrib.auth import get_user_model
from flashcards.forms import FlashcardReviewForm
from decks.models import Deck
from flashcards.models import Flashcard

User = get_user_model()


class FlashcardReviewFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="form_user",
            password="secret123",
        )
        self.client.login(username="form_user", password="secret123")
        self.deck = Deck.objects.create(name="Test Deck", owner=self.user)
        self.flashcard = Flashcard.objects.create(
            question="Test question",
            answer_a="A",
            answer_b="B",
            answer_c="C",
            answer_d="D",
            correct_answer="A",
            deck=self.deck,
            created_by=self.user,
        )

    def test_form_sets_choices_from_flashcard(self):
        form = FlashcardReviewForm(flashcard=self.flashcard)

        choices = form.fields["selected_answer"].choices

        self.assertEqual(len(choices), 4)
        self.assertIn(
            (self.flashcard.answer_a, self.flashcard.answer_a), choices
        )
        self.assertIn(
            (self.flashcard.answer_b, self.flashcard.answer_b), choices
        )

    def test_shuffle_only_on_get(self):
        form1 = FlashcardReviewForm(flashcard=self.flashcard)
        form2 = FlashcardReviewForm(flashcard=self.flashcard)

        choices1 = form1.fields["selected_answer"].choices
        choices2 = form2.fields["selected_answer"].choices

        self.assertCountEqual(choices1, choices2)

    def test_no_shuffle_on_post(self):
        data = {"selected_answer": self.flashcard.answer_a}

        form1 = FlashcardReviewForm(data=data, flashcard=self.flashcard)
        form2 = FlashcardReviewForm(data=data, flashcard=self.flashcard)

        choices1 = form1.fields["selected_answer"].choices
        choices2 = form2.fields["selected_answer"].choices

        self.assertEqual(choices1, choices2)

    def test_valid_form(self):
        data = {"selected_answer": self.flashcard.answer_a}

        form = FlashcardReviewForm(data=data, flashcard=self.flashcard)

        self.assertTrue(form.is_valid())

    def test_invalid_choice(self):
        data = {"selected_answer": "WRONG"}

        form = FlashcardReviewForm(data=data, flashcard=self.flashcard)

        self.assertFalse(form.is_valid())
        self.assertIn("selected_answer", form.errors)
