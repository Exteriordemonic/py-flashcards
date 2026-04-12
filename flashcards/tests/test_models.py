from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from decks.models import Deck
from flashcards.models import Answer, Flashcard, FlashcardUserState
from flashcards.services import AnswerInput, FlashcardService

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        username="flashcard_owner",
        password="secret123",
    )


@pytest.fixture
def deck(user):
    return Deck.objects.create(name="Owner Deck", owner=user)


@pytest.fixture
def flashcard(user, deck):
    return Flashcard.objects.create(
        question="What is capitol of Poland?",
        deck=deck,
        created_by=user,
    )


def test_created_by_set_null_when_user_deleted():
    # Deck.owner CASCADE-deletes decks when the owner is removed, so the creator
    # must differ from the deck owner to observe SET_NULL on created_by.
    deck_owner = User.objects.create_user(
        username="deck_owner",
        password="secret123",
    )
    creator = User.objects.create_user(
        username="card_creator",
        password="secret123",
    )
    deck = Deck.objects.create(name="Owner Deck", owner=deck_owner)
    flashcard = Flashcard.objects.create(
        question="What is capitol of Poland?",
        deck=deck,
        created_by=creator,
    )

    creator.delete()
    flashcard.refresh_from_db()

    assert flashcard.created_by is None


def test_flashcard_user_state_unique_for_flashcard_and_user(flashcard, user):
    FlashcardUserState.objects.create(
        flashcard=flashcard,
        user=user,
        next_review_at=date(2026, 4, 9),
    )

    with pytest.raises(IntegrityError):
        FlashcardUserState.objects.create(
            flashcard=flashcard,
            user=user,
            next_review_at=date(2026, 4, 10),
        )


def test_flashcard_unique_per_question_created_by_and_deck(user, deck):
    question = "Same question twice"
    Flashcard.objects.create(
        question=question,
        deck=deck,
        created_by=user,
    )

    with pytest.raises(IntegrityError):
        Flashcard.objects.create(
            question=question,
            deck=deck,
            created_by=user,
        )


def test_answer_defaults_and_links_to_flashcard(flashcard):
    answer = Answer.objects.create(flashcard=flashcard, text="Option A")

    assert answer.is_correct is False
    assert list(flashcard.answers.values_list("text", flat=True)) == ["Option A"]


def test_answers_deleted_when_flashcard_deleted(user, deck):
    flashcard = FlashcardService.create_flashcard(
        question="Cascade test",
        created_by=user,
        deck=deck,
        answers=[
            AnswerInput(text="Yes", is_correct=True),
            AnswerInput(text="No"),
        ],
    )
    answer_ids = set(flashcard.answers.values_list("pk", flat=True))

    flashcard.delete()

    assert Answer.objects.filter(pk__in=answer_ids).count() == 0
