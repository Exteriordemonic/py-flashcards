import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("decks", "0001_initial"),
        ("flashcards", "0008_merge_20260409_1549"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="Deck"),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="flashcard",
                    name="deck",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="flashcards",
                        to="decks.deck",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
