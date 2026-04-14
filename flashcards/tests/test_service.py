from collections import Counter

import pytest
from django.contrib.auth import get_user_model
from django.db import transaction


from decks.models import Deck
from flashcards.models import Flashcard, Review
from flashcards.services import AnswerInput, FlashcardService, RepetitionService

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="user1",
        password="password1",
    )


@pytest.fixture
def deck(user):
    return Deck.objects.create(name="Deck Name", owner=user)


@pytest.fixture
def flashcard_create_data(user, deck):
    return {
        "question": "Capitol of Poland?",
        "created_by": user,
        "deck": deck,
        "answers": make_answers(),
    }


@pytest.fixture
def flashcard(flashcard_create_data):
    return FlashcardService.create_flashcard(**flashcard_create_data)


@pytest.fixture
def flashcard_user_state(flashcard):
    return FlashcardService.get_or_create_flashcard_user_state(flashcard)


def make_answers():
    return [
        AnswerInput(text="Warsaw", is_correct=True),
        AnswerInput(text="Paris"),
        AnswerInput(text="Berlin"),
    ]


def test_creating_flashcard(user, deck):
    flashcard = FlashcardService.create_flashcard(
        question="Capitol of Poland?",
        created_by=user,
        deck=deck,
        answers=[
            AnswerInput(text="Warsaw", is_correct=True),
            AnswerInput(text="Paris"),
            AnswerInput(text="Berlin"),
        ],
    )

    assert flashcard.question == "Capitol of Poland?"
    assert flashcard.created_by == user
    assert flashcard.deck == deck
    assert flashcard.answers.count() == 3
    assert flashcard.answers.filter(text="Warsaw", is_correct=True).exists()


def test_correct_data(flashcard_create_data):
    flashcard = FlashcardService.create_flashcard(**flashcard_create_data)

    assert flashcard.question == flashcard_create_data["question"]
    assert flashcard.answers.count() == len(flashcard_create_data["answers"])
    assert flashcard.deck == flashcard_create_data["deck"]
    assert flashcard.created_by == flashcard_create_data["created_by"]

    correct_answers = flashcard.answers.filter(is_correct=True)
    assert correct_answers.count() == 1

    assert flashcard.answers.filter(text="Warsaw", is_correct=True).exists()

    texts = list(flashcard.answers.values_list("text", flat=True))
    assert Counter(texts) == Counter(["Warsaw", "Paris", "Berlin"])


def test_deck_from_string(flashcard_create_data, user):
    data = {**flashcard_create_data, "deck": "deck"}

    flashcard = FlashcardService.create_flashcard(**data)
    assert flashcard.deck.name == "deck"
    assert Deck.objects.count() == 2

    assert Deck.objects.filter(name="deck", owner=user).exists()


def test_deck_from_string_that_exists(flashcard_create_data, deck):
    data = {**flashcard_create_data, "deck": "Deck Name"}

    flashcard = FlashcardService.create_flashcard(**data)

    assert flashcard.deck == deck
    assert Deck.objects.count() == 1


def test_data_without_answers(flashcard_create_data):
    data = {**flashcard_create_data, "answers": []}
    with pytest.raises(ValueError):
        FlashcardService.create_flashcard(**data)


def test_data_without_correct_answers(flashcard_create_data):
    data = {
        **flashcard_create_data,
        "answers": [AnswerInput(text=a.text, is_correct=False) for a in flashcard_create_data["answers"]],
    }

    with pytest.raises(ValueError):
        FlashcardService.create_flashcard(**data)


def test_all_correct_answers(flashcard_create_data):
    data = {
        **flashcard_create_data,
        "answers": [AnswerInput(text=a.text, is_correct=True) for a in flashcard_create_data["answers"]],
    }

    flashcard = FlashcardService.create_flashcard(**data)
    assert flashcard.answers.filter(is_correct=True).count() == len(data["answers"])


def test_multiple_correct_answers(flashcard_create_data):
    orig = flashcard_create_data["answers"]
    data = {
        **flashcard_create_data,
        "answers": [
            orig[0],
            AnswerInput(text=orig[1].text, is_correct=True),
            orig[2],
        ],
    }

    correct_answers = len([answer for answer in data["answers"] if answer.is_correct])

    flashcard = FlashcardService.create_flashcard(**data)
    assert flashcard.answers.filter(is_correct=True).count() == correct_answers


def test_no_flashcard_created_when_answers_none(flashcard_create_data):
    data = {**flashcard_create_data, "answers": None}

    with pytest.raises(ValueError, match="Answers are required"):
        FlashcardService.create_flashcard(**data)

    assert Flashcard.objects.count() == 0


def test_update_flashcard_happy_path(flashcard):
    # Arrange
    answers = [
        AnswerInput("Asnwer 1"),
        AnswerInput("Asnwer 2"),
        AnswerInput("Asnwer 3"),
        AnswerInput("Asnwer 4", True),
    ]

    # Act
    flashcard = FlashcardService.update_flashcard(flashcard=flashcard, answers=answers)

    # Assert
    assert flashcard.answers.count() == 4
    assert flashcard.answers.filter(is_correct=True).count() == 1

    texts = list(flashcard.answers.order_by("pk").values_list("text", flat=True))
    assert texts == ["Asnwer 1", "Asnwer 2", "Asnwer 3", "Asnwer 4"]


def test_update_flashcard_with_deck(flashcard):
    # Arrange
    deck = Deck.objects.create(name="Deck Name 2", owner=flashcard.created_by)

    # Act
    flashcard = FlashcardService.update_flashcard(flashcard=flashcard, deck=deck)

    # Assert
    assert flashcard.deck == deck


def test_update_flashcard_with_(flashcard):
    # Arrange
    question = "What is the capital of France?"

    # Act
    flashcard = FlashcardService.update_flashcard(flashcard=flashcard, question=question)

    # Assert
    assert flashcard.question == question


def test_update_flashcard_with_incorrect_answers(flashcard):
    # Arrange
    answers = []

    # Act + Assert
    with pytest.raises(ValueError, match="Answers are required"):
        FlashcardService.update_flashcard(flashcard=flashcard, answers=answers)


def test_create_review_happy_path(flashcard):
    # Arrange
    quality = Review.Quality.PERFECT

    # Act
    FlashcardService.create_review(flashcard=flashcard, quality=quality)
    FlashcardService.create_review(flashcard=flashcard, quality=quality)
    FlashcardService.create_review(flashcard=flashcard, quality=quality)

    # Assert
    assert Review.objects.filter(flashcard=flashcard).count() == 3
    assert Review.objects.last().quality == quality


@pytest.mark.django_db(transaction=True)
def test_create_review_no_quality(flashcard):
    # Arrange
    quality = None

    # Act + Assert
    with pytest.raises(Exception):
        FlashcardService.create_review(flashcard=flashcard, quality=quality)

    # Assert
    assert Review.objects.filter(flashcard=flashcard).count() == 0
