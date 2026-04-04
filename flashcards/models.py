from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Flashcard(models.Model):
    """
    # Flashcard model with fields for question, answers (A-D),
    # and the correct answer.
    # The 'created_by' field can be null if the user deletes their account,
    # but the flashcard remains available for other users.
    """

    question = models.CharField(max_length=255)
    answer_a = models.CharField(max_length=255)
    answer_b = models.CharField(max_length=255)
    answer_c = models.CharField(max_length=255)
    answer_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deck = models.ManyToManyField(to="Deck", related_name="flashcards")
    created_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name="flashcards",
        null=True,
        blank=True,
    )


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
    # Captures user, flashcard, deck, review quality, and review date.
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
    deck = models.ForeignKey(
        to="Deck",
        on_delete=models.SET_NULL,
        null=True,
        related_name="reviews",
    )
    quality = models.IntegerField(choices=Quality.choices)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Deck(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="decks"
    )
    members = models.ManyToManyField(to=User, related_name="decks_member")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.members.filter(id=self.owner_id).exists():
            self.members.add(self.owner)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "owner"],
                name="unique_deck_user_name",
            )
        ]
