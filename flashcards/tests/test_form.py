from collections import Counter

import pytest
from django.contrib.auth import get_user_model

from decks.models import Deck
from flashcards.forms import FlashcardReviewForm
from flashcards.services import AnswerInput, FlashcardService

User = get_user_model()

pytestmark = pytest.mark.django_db

_FORM_ANSWER_TEXTS = ("A", "B", "C", "D")


@pytest.fixture
def form_user(db):
    return User.objects.create_user(
        username="form_user",
        password="secret123",
    )


@pytest.fixture
def form_deck(form_user):
    return Deck.objects.create(name="Test Deck", owner=form_user)


@pytest.fixture
def form_flashcard(form_user, form_deck):
    first, *rest = _FORM_ANSWER_TEXTS
    return FlashcardService.create_flashcard(
        question="Test question",
        created_by=form_user,
        deck=form_deck,
        answers=[
            AnswerInput(text=first, is_correct=True),
            *[AnswerInput(text=t) for t in rest],
        ],
    )


def test_form_sets_choices_from_flashcard(form_flashcard):
    form = FlashcardReviewForm(flashcard=form_flashcard)

    choices = form.fields["selected_answer"].choices

    assert len(choices) == 4
    assert (_FORM_ANSWER_TEXTS[0], _FORM_ANSWER_TEXTS[0]) in choices
    assert (_FORM_ANSWER_TEXTS[1], _FORM_ANSWER_TEXTS[1]) in choices


def test_shuffle_only_on_get(form_flashcard):
    form1 = FlashcardReviewForm(flashcard=form_flashcard)
    form2 = FlashcardReviewForm(flashcard=form_flashcard)

    choices1 = form1.fields["selected_answer"].choices
    choices2 = form2.fields["selected_answer"].choices

    assert Counter(choices1) == Counter(choices2)


def test_no_shuffle_on_post(form_flashcard):
    data = {"selected_answer": _FORM_ANSWER_TEXTS[0]}

    form1 = FlashcardReviewForm(data=data, flashcard=form_flashcard)
    form2 = FlashcardReviewForm(data=data, flashcard=form_flashcard)

    choices1 = form1.fields["selected_answer"].choices
    choices2 = form2.fields["selected_answer"].choices

    assert choices1 == choices2


def test_valid_form(form_flashcard):
    data = {"selected_answer": _FORM_ANSWER_TEXTS[0]}

    form = FlashcardReviewForm(data=data, flashcard=form_flashcard)

    assert form.is_valid()


def test_invalid_choice(form_flashcard):
    data = {"selected_answer": "WRONG"}

    form = FlashcardReviewForm(data=data, flashcard=form_flashcard)

    assert not form.is_valid()
    assert "selected_answer" in form.errors


def test_create_flashcard_from():
    pass
