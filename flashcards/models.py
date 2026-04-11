from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Flashcard(models.Model):
    """
    Example of how to create a Flashcard object:
        Flashcard.objects.create(
            question="Question text",
            deck=deck,
            created_by=user
        )

    Fields:
        question : str — the flashcard question (required)
        deck : Deck — the deck to which this flashcard belongs (required)
        created_by : User — the user who created this flashcard (optional)

    Note: The combination of question, created_by,
    and deck must be unique per flashcard.
    """

    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deck = models.ForeignKey(
        to="decks.Deck",
        on_delete=models.CASCADE,
        related_name="flashcards",
    )
    created_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name="flashcards",
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "created_by", "deck"],
                name="unique_flashcard_created_by_question_deck",
            )
        ]


class FlashcardUserState(models.Model):
    """
    # FlashcardUserState tracks user progress on each card.
    # 'ease_factor' is recall ease; higher values mean longer gaps
    # between reviews.
    """

    flashcard = models.ForeignKey(
        to=Flashcard,
        on_delete=models.CASCADE,
        related_name="flashcard_states",
    )
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="flashcard_states"
    )
    ease_factor = models.FloatField(default=2.5)
    next_review_at = models.DateField()
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["flashcard", "user"],
                name="unique_flashcard_user_state",
            )
        ]


class Review(models.Model):
    """
    # Review model: records when and how well a user reviewed a flashcard.
    # Captures user, flashcard, review quality, and review date.
    """

    class Quality(models.IntegerChoices):
        HARD = 1, "Hard"
        NORMAL = 2, "Normal"
        EASY = 3, "Easy"
        VERY_EASY = 4, "Very Easy"
        PERFECT = 5, "Perfect"

    flashcard = models.ForeignKey(
        to=Flashcard,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="reviews"
    )
    quality = models.IntegerField(choices=Quality.choices)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Answer(models.Model):
    flashcard = models.ForeignKey(
        Flashcard, on_delete=models.CASCADE, related_name="answers"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
