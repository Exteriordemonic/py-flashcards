import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from decks.models import Deck
from flashcards.models import Flashcard, Review
from flashcards.services import AnswerInput, FlashcardService

User = get_user_model()


@pytest.fixture
def view_user(db):
    return User.objects.create_user(username="view_user", password="secret123")


@pytest.fixture
def view_user2(db):
    return User.objects.create_user(username="view_user2", password="secret123")


@pytest.fixture
def view_deck(view_user):
    return Deck.objects.create(name="Math", owner=view_user)


@pytest.fixture
def view_flashcard(view_user, view_deck):
    return FlashcardService.create_flashcard(
        question="2 + 2 = ?",
        created_by=view_user,
        deck=view_deck,
        answers=[
            AnswerInput(text="3"),
            AnswerInput(text="4", is_correct=True),
            AnswerInput(text="5"),
            AnswerInput(text="6"),
        ],
    )


@pytest.fixture
def client_as_view_user(client, view_user):
    client.force_login(view_user)
    return client


def test_flashcard_list_view_for_logged_user(client_as_view_user):
    response = client_as_view_user.get(reverse("flashcards:flashcard-list"))
    assert response.status_code == 200


def test_flashcard_list_view_requires_login(client):
    response = client.get(reverse("flashcards:flashcard-list"))
    assert response.status_code == 302


def test_flashcard_create_view_creates_object(client_as_view_user, view_deck):
    response = client_as_view_user.post(
        reverse("flashcards:flashcard-create"),
        data={
            "question": "Capital of France?",
            "deck": view_deck.id,
        },
    )
    assert response.status_code == 302
    flashcard = Flashcard.objects.get(question="Capital of France?")
    assert flashcard.deck == view_deck
    # CreateView form only has question + deck; Answer rows are added elsewhere (e.g. admin / service).
    assert flashcard.answers.count() == 0


def test_flashcard_delete_view_deletes_object(client_as_view_user, view_flashcard):
    response = client_as_view_user.post(
        reverse(
            "flashcards:flashcard-delete",
            kwargs={"pk": view_flashcard.id},
        )
    )
    assert response.status_code == 302
    assert not Flashcard.objects.filter(id=view_flashcard.id).exists()


def test_deck_create_view_creates_object(client_as_view_user, view_user):
    response = client_as_view_user.post(
        reverse("decks:deck-create"),
        data={
            "name": "Geography",
        },
    )
    assert response.status_code == 302
    deck = Deck.objects.get(name="Geography")
    assert deck.owner == view_user


def test_deck_delete_view_deletes_object(client_as_view_user, view_deck):
    response = client_as_view_user.post(
        reverse("decks:deck-delete", kwargs={"pk": view_deck.id})
    )
    assert response.status_code == 302
    assert not Deck.objects.filter(id=view_deck.id).exists()


def test_flashcard_list_shows_only_current_user_flashcards(
    client_as_view_user, view_user, view_user2, view_flashcard
):
    Flashcard.objects.create(
        question="Question owned by user2",
        deck=Deck.objects.create(name="User2 Deck", owner=view_user2),
        created_by=view_user2,
    )
    response = client_as_view_user.get(reverse("flashcards:flashcard-list"))

    assert response.status_code == 200
    assert view_flashcard.question.encode() in response.content
    assert b"Question owned by user2" not in response.content


def test_flashcard_list_show_correct_data_for_decks(
    client_as_view_user, view_user, view_deck
):
    Flashcard.objects.create(
        question="Second question in same deck",
        deck=view_deck,
        created_by=view_user,
    )

    response = client_as_view_user.get(reverse("flashcards:flashcard-list"))
    assert response.status_code == 200
    assert view_deck.name.encode() in response.content


def test_deck_detail_view_that_is_not_owner(client, view_user2, view_deck):
    client.force_login(view_user2)

    response = client.get(
        reverse("decks:deck-detail", kwargs={"pk": view_deck.id})
    )
    assert response.status_code == 404


def test_deck_show_only_owner_flashcards_on_deck(
    client_as_view_user, view_user, view_user2, view_deck
):
    Flashcard.objects.create(
        question="Question for user 2",
        deck=view_deck,
        created_by=view_user2,
    )

    response = client_as_view_user.get(
        reverse("decks:deck-detail", kwargs={"pk": view_deck.id})
    )
    assert response.status_code == 200
    assert "Question for user 2" not in response.content.decode()


@pytest.fixture
def review_user(db):
    return User.objects.create_user(username="view_user", password="secret123")


@pytest.fixture
def review_flashcard(review_user):
    deck = Deck.objects.create(name="Geography", owner=review_user)
    return FlashcardService.create_flashcard(
        question="Capital of Poland?",
        created_by=review_user,
        deck=deck,
        answers=[
            AnswerInput(text="Warsaw", is_correct=True),
            AnswerInput(text="Berlin"),
            AnswerInput(text="Krakow"),
            AnswerInput(text="Prague"),
        ],
    )


@pytest.fixture
def client_review(client, review_user):
    client.force_login(review_user)
    return client


def test_review_view_flashcard_without_answers(client_review, review_user):
    deck = Deck.objects.create(name="Solo Deck", owner=review_user)
    flashcard = Flashcard.objects.create(
        question="Question only",
        deck=deck,
        created_by=review_user,
    )
    url = reverse("flashcards:flashcard-review", kwargs={"pk": flashcard.id})
    response = client_review.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "Question only" in content
    assert response.context["form"].fields["selected_answer"].choices == []


def test_review_view_displays_question_and_options(client_review, review_flashcard):
    url = reverse(
        "flashcards:flashcard-review", kwargs={"pk": review_flashcard.id}
    )
    response = client_review.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "Capital of Poland?" in content
    assert "Warsaw" in content
    assert "Berlin" in content
    assert "Krakow" in content
    assert "Prague" in content


def test_review_view_allows_answer_submission_and_feedback(
    client_review, review_flashcard
):
    url = reverse(
        "flashcards:flashcard-review", kwargs={"pk": review_flashcard.id}
    )

    response = client_review.post(url, {"selected_answer": "Warsaw"})
    assert response.status_code == 200
    assert "correct" in response.content.decode().lower()

    response = client_review.post(url, {"selected_answer": "Berlin"})
    assert response.status_code == 200
    assert "incorrect" in response.content.decode().lower()


def test_review_created_after_post(client_review, review_user, review_flashcard):
    url = reverse("flashcards:flashcard-review", args=[review_flashcard.id])

    correct_text = review_flashcard.answers.filter(is_correct=True).values_list(
        "text", flat=True
    ).first()
    client_review.post(url, data={"selected_answer": correct_text})

    assert Review.objects.count() == 1

    review = Review.objects.first()

    assert review.user == review_user
    assert review.flashcard == review_flashcard
