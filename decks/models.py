from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Deck(models.Model):
    """
    Example of how to create a Deck object:
        Deck.objects.create(name="Deck Name", owner=user)

    Fields:
        name : str — the name of the deck (required)
        owner : User — the owner of the deck (required, User model instance)

    Note: The deck name must be unique for each owner.
    """

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="decks")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "flashcards_deck"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "owner"],
                name="unique_deck_user_name",
            )
        ]
