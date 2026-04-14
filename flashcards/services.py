from dataclasses import dataclass
import stat
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import datetime, timedelta


from flashcards.models import Flashcard, Answer, FlashcardUserState, Review
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
        question: str | None = None,
        deck: Deck | None = None,
        answers: list[AnswerInput] | None = None,
    ) -> Flashcard:
        with transaction.atomic():
            if question:
                flashcard.question = question
            if deck:
                flashcard.deck = deck

            # Only save if question or deck was changed
            if question or deck:
                flashcard.save()

            # Only update answers if explicitly provided (not None)
            if answers is not None:
                _validate_answers(answers)
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

    def create_review(flashcard: Flashcard, quality: Review.Quality):
        Review.objects.create(
            flashcard=flashcard,
            user=flashcard.created_by,
            quality=quality,
        )

    @staticmethod
    def get_or_create_flashcard_user_state(
        flashcard: Flashcard,
    ):
        if not flashcard:
            raise ValueError("Flashcard is required")

        today = datetime.now()

        return FlashcardUserState.objects.get_or_create(
            flashcard=flashcard, user=flashcard.created_by, last_reviewed_at=today
        )

    @staticmethod
    def review_flashcard(flashcard: Flashcard, quality: Review.Quality) -> FlashcardUserState:
        FlashcardService.create_review(flashcard, quality)
        state = FlashcardService.get_or_create_flashcard_user_state(flashcard)
        return state


class RepetitionService:
    @staticmethod
    def compute_next_review(flashcard_user_state=FlashcardUserState):
        pass

    @staticmethod
    def get_intervals(flashcard):
        return 1
