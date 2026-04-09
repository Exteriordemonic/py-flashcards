import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "flashcards",
            "0005_remove_deck_members_remove_flashcard_deck_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="flashcard",
            name="deck",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flashcards",
                to="flashcards.deck",
            ),
        ),
    ]
