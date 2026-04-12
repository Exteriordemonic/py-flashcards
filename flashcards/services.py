from dataclasses import dataclass
from django.contrib.auth import get_user_model
from django.db import transaction


from flashcards.models import Flashcard, Answer
from decks.models import Deck

User = get_user_model()


@dataclass
class AnswerInput:
    text: str
    is_correct: bool = False


def _validate_answers(answers: list[AnswerInput]) -> None:
    if not answers:
        raise ValueError("Answers are required")

    if not any(a.is_correct for a in answers):
        raise ValueError("At least one answer should be True")


class FlashcardService:
    @staticmethod
    def create_flashcard(
        question: str,
        created_by: User,
        deck: Deck | str,
        answers: list[AnswerInput],
    ) -> Flashcard:
        _validate_answers(answers)

        with transaction.atomic():
            if not isinstance(deck, Deck):
                deck, _ = Deck.objects.get_or_create(name=deck, owner=created_by)

            flashcard = Flashcard.objects.create(question=question, created_by=created_by, deck=deck)

            Answer.objects.bulk_create(
                [
                    Answer(
                        text=a.text,
                        is_correct=a.is_correct,
                        flashcard=flashcard,
                    )
                    for a in answers
                ]
            )
            return flashcard

    @staticmethod
    def update_flashcard(
        flashcard: Flashcard,
        question: str,
        deck: Deck,
        answers: list[AnswerInput],
    ) -> Flashcard:
        _validate_answers(answers)

        with transaction.atomic():
            flashcard.question = question
            flashcard.deck = deck
            flashcard.save()
            flashcard.answers.all().delete()
            Answer.objects.bulk_create(
                [
                    Answer(
                        text=a.text,
                        is_correct=a.is_correct,
                        flashcard=flashcard,
                    )
                    for a in answers
                ]
            )
        return flashcard
