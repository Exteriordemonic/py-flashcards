from decks.models import Deck
from flashcards.services import AnswerInput, FlashcardService


def make_flashcard_with_answers(
    user,
    *,
    question="What is the capital of Poland?",
    deck=None,
    deck_owner=None,
):
    owner = deck_owner if deck_owner is not None else user
    if deck is None:
        deck = Deck.objects.create(name="Example Deck 1", owner=owner)
    return FlashcardService.create_flashcard(
        question=question,
        created_by=user,
        deck=deck,
        answers=[
            AnswerInput(text="London"),
            AnswerInput(text="Berlin"),
            AnswerInput(text="Warsaw", is_correct=True),
            AnswerInput(text="Paris"),
        ],
    )
