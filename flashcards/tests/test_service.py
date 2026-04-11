from django.contrib.auth import get_user_model
from django.test import TestCase

from decks.models import Deck
from flashcards.models import Flashcard
from flashcards.services import FlashcardService, AnswerInput

User = get_user_model()


class FlashcardServiceTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="user1", password="password1"
        )
        self.deck = Deck.objects.create(name="Deck Name", owner=self.user)

        self.data = {
            "question": "Capitol of Poland?",
            "created_by": self.user,
            "deck": self.deck,
            "answers": [
                AnswerInput(text="Warsaw", is_correct=True),
                AnswerInput(text="Paris"),
                AnswerInput(text="Berlin"),
            ],
        }

    def test_correct_data(self):
        flashcard = FlashcardService.create_flashcard(**self.data)

        self.assertEqual(flashcard.question, self.data["question"])
        self.assertEqual(flashcard.answers.count(), len(self.data["answers"]))
        self.assertEqual(flashcard.deck, self.data["deck"])
        self.assertEqual(flashcard.created_by, self.data["created_by"])

        correct_answers = flashcard.answers.filter(is_correct=True)
        self.assertEqual(correct_answers.count(), 1)

        self.assertTrue(
            flashcard.answers.filter(text="Warsaw", is_correct=True).exists()
        )

        texts = list(flashcard.answers.values_list("text", flat=True))
        self.assertCountEqual(texts, ["Warsaw", "Paris", "Berlin"])

    def test_deck_from_string(self):
        data = {**self.data, "deck": "deck"}

        flashcard = FlashcardService.create_flashcard(**data)
        self.assertEqual(flashcard.deck.name, "deck")
        self.assertEqual(Deck.objects.count(), 2)

        self.assertTrue(
            Deck.objects.filter(name="deck", owner=self.user).exists()
        )

    def test_deck_from_string_that_exists(self):
        data = {**self.data, "deck": "Deck Name"}

        flashcard = FlashcardService.create_flashcard(**data)

        self.assertEqual(flashcard.deck, self.deck)
        self.assertEqual(Deck.objects.count(), 1)

    def test_data_without_answers(self):
        data = {**self.data, "answers": []}
        with self.assertRaises(ValueError):
            FlashcardService.create_flashcard(**data)

    def test_data_without_correct_answers(self):
        data = {
            **self.data,
            "answers": [
                AnswerInput(text=a.text, is_correct=False)
                for a in self.data["answers"]
            ],
        }

        with self.assertRaises(ValueError):
            FlashcardService.create_flashcard(**data)

    def test_all_correct_answers(self):
        data = {
            **self.data,
            "answers": [
                AnswerInput(text=a.text, is_correct=True)
                for a in self.data["answers"]
            ],
        }

        flashcard = FlashcardService.create_flashcard(**data)
        self.assertEqual(
            flashcard.answers.filter(is_correct=True).count(),
            len(data["answers"]),
        )

    def test_multiple_correct_answers(self):
        orig = self.data["answers"]
        data = {
            **self.data,
            "answers": [
                orig[0],
                AnswerInput(text=orig[1].text, is_correct=True),
                orig[2],
            ],
        }

        correct_answers = len(
            [answer for answer in data["answers"] if answer.is_correct]
        )

        flashcard = FlashcardService.create_flashcard(**data)
        self.assertEqual(
            flashcard.answers.filter(is_correct=True).count(),
            correct_answers,
        )

    def test_no_flashcard_created_when_answers_invalid(self):
        data = {**self.data, "answers": None}

        with self.assertRaises(Exception):
            FlashcardService.create_flashcard(**data)

        self.assertEqual(Flashcard.objects.count(), 0)
