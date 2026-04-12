import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from decks.models import Deck

from flashcards.tests.helpers import make_flashcard_with_answers

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture
def user2(db):
    return User.objects.create_user(username="testuser2", password="testpassword2")


@pytest.fixture
def client_as_user(client, user):
    client.force_login(user)
    return client


def test_flashcard_list_is_resolved(client_as_user):
    response = client_as_user.get(reverse("flashcards:flashcard-list"))
    assert response.status_code == 200


def test_flashcard_detail_is_resolved(client_as_user, user):
    flashcard = make_flashcard_with_answers(user)

    response = client_as_user.get(
        reverse("flashcards:flashcard-detail", kwargs={"pk": flashcard.id})
    )
    assert response.status_code == 200


def test_flashcard_create_is_resolved(client_as_user):
    response = client_as_user.get(reverse("flashcards:flashcard-create"))
    assert response.status_code == 200


def test_flashcard_update_is_resolved(client_as_user, user):
    flashcard = make_flashcard_with_answers(user)

    response = client_as_user.get(
        reverse("flashcards:flashcard-update", kwargs={"pk": flashcard.id})
    )
    assert response.status_code == 200


def test_flashcard_delete_is_resolved(client_as_user, user):
    flashcard = make_flashcard_with_answers(user)

    response = client_as_user.get(
        reverse("flashcards:flashcard-delete", kwargs={"pk": flashcard.id})
    )
    assert response.status_code == 200


def test_deck_list_is_resolved(client_as_user):
    response = client_as_user.get(reverse("decks:deck-list"))
    assert response.status_code == 200


def test_deck_detail_is_resolved(client_as_user, user):
    deck = Deck.objects.create(name="Example Deck 1", owner=user)

    response = client_as_user.get(reverse("decks:deck-detail", kwargs={"pk": deck.id}))
    assert response.status_code == 200


def test_deck_create_is_resolved(client_as_user):
    response = client_as_user.get(reverse("decks:deck-create"))
    assert response.status_code == 200


def test_deck_update_is_resolved(client_as_user, user):
    deck = Deck.objects.create(name="Example Deck 1", owner=user)

    response = client_as_user.get(reverse("decks:deck-update", kwargs={"pk": deck.id}))
    assert response.status_code == 200


def test_deck_delete_is_resolved(client_as_user, user):
    deck = Deck.objects.create(name="Example Deck 1", owner=user)

    response = client_as_user.get(reverse("decks:deck-delete", kwargs={"pk": deck.id}))
    assert response.status_code == 200


def test_not_logged_in_access(client, user):
    flashcard = make_flashcard_with_answers(user)
    deck = flashcard.deck
    urls = [
        reverse("flashcards:flashcard-list"),
        reverse("flashcards:flashcard-create"),
        reverse("flashcards:flashcard-detail", kwargs={"pk": flashcard.id}),
        reverse("flashcards:flashcard-update", kwargs={"pk": flashcard.id}),
        reverse("flashcards:flashcard-delete", kwargs={"pk": flashcard.id}),
        reverse("decks:deck-list"),
        reverse("decks:deck-create"),
        reverse("decks:deck-detail", kwargs={"pk": deck.id}),
        reverse("decks:deck-update", kwargs={"pk": deck.id}),
        reverse("decks:deck-delete", kwargs={"pk": deck.id}),
    ]

    for url in urls:
        assert client.get(url).status_code == 302


def test_redirect_if_user_have_no_access_to_the_deck(client, user, user2):
    deck = Deck.objects.create(name="Example Deck 1", owner=user)

    client.force_login(user2)
    response = client.get(reverse("decks:deck-detail", kwargs={"pk": deck.id}))

    assert response.status_code == 404


def test_redirect_if_user_tries_to_delete_not_owned_deck(client, user, user2):
    deck = Deck.objects.create(name="Example Deck 1", owner=user)

    client.force_login(user2)
    response = client.get(reverse("decks:deck-delete", kwargs={"pk": deck.id}))

    assert response.status_code == 404


def test_redirect_if_user_tries_to_update_not_owned_deck(client, user, user2):
    deck = Deck.objects.create(name="Example Deck 1", owner=user)

    client.force_login(user2)
    response = client.get(reverse("decks:deck-update", kwargs={"pk": deck.id}))

    assert response.status_code == 404


def test_redirect_if_user_tries_to_view_not_owned_flashcard(client, user, user2):
    flashcard = make_flashcard_with_answers(user)

    client.force_login(user2)
    response = client.get(
        reverse("flashcards:flashcard-detail", kwargs={"pk": flashcard.id})
    )

    assert response.status_code == 404


def test_redirect_if_user_tries_to_update_not_owned_flashcard(client, user, user2):
    flashcard = make_flashcard_with_answers(user)

    client.force_login(user2)
    response = client.get(
        reverse("flashcards:flashcard-update", kwargs={"pk": flashcard.id})
    )

    assert response.status_code == 404


def test_redirect_if_user_tries_to_delete_not_owned_flashcard(client, user, user2):
    flashcard = make_flashcard_with_answers(user)

    client.force_login(user2)
    response = client.get(
        reverse("flashcards:flashcard-delete", kwargs={"pk": flashcard.id})
    )

    assert response.status_code == 404


def test_review_flashcard(client_as_user, user):
    flashcard = make_flashcard_with_answers(user)

    response = client_as_user.get(
        reverse("flashcards:flashcard-review", kwargs={"pk": flashcard.id})
    )

    assert response.status_code == 200


def test_review_flashcard_without_access_returns_404(client, user, user2):
    flashcard = make_flashcard_with_answers(user)

    client.force_login(user2)

    response = client.get(
        reverse("flashcards:flashcard-review", kwargs={"pk": flashcard.id})
    )

    assert response.status_code == 404
