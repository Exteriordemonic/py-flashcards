from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    We are using AbstractUser to create a custom user model that will
    be set as the default user in settings.py. This makes it easier to
    extend or modify the user with additional functionality in the future.
    """

    pass
