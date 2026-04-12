from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Flashcard(models.Model):
    """
    Represents a flashcard in the system. The combination of question,
    created_by, and deck must be unique per flashcard.

    Attributes:
        question (CharField): The flashcard question.
        created_at (DateTimeField): When the flashcard was created.
        updated_at (DateTimeField): When the flashcard was last updated.
        deck (ForeignKey): The deck this flashcard belongs to.
        created_by (ForeignKey): The user who created this flashcard, if any.
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
    Represents per-user spaced-repetition state for a flashcard. The ease_factor
    reflects recall ease; higher values imply longer gaps between reviews.

    Attributes:
        flashcard (ForeignKey): The flashcard being tracked.
        user (ForeignKey): The learner whose progress is stored.
        ease_factor (FloatField): Recall ease; default 2.5.
        next_review_at (DateField): When the card is due for review.
        last_reviewed_at (DateTimeField): When the user last reviewed, if ever.
    """

    flashcard = models.ForeignKey(
        to=Flashcard,
        on_delete=models.CASCADE,
        related_name="flashcard_states",
    )
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="flashcard_states")
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
    Represents a single review event: when and how well a user rated a flashcard.

    Attributes:
        flashcard (ForeignKey): The flashcard that was reviewed.
        user (ForeignKey): The user who performed the review.
        quality (IntegerField): Self-reported difficulty using Quality choices.
        reviewed_at (DateTimeField): When the review was recorded.
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
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="reviews")
    quality = models.IntegerField(choices=Quality.choices)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Answer(models.Model):
    """
    Represents one answer option for a flashcard. Each flashcard should have
    exactly one answer marked as correct.

    Attributes:
        flashcard (ForeignKey): The flashcard this answer belongs to.
        text (CharField): The answer text (max 255 characters).
        is_correct (BooleanField): Whether this is the correct answer.
    """

    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255, blank=False)
    is_correct = models.BooleanField(default=False)
