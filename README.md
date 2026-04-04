# Hello there

How to setup django project?

1. ✅ Install the venv

   `python -m venv venv`

2. ✅ Activate venv (Windows)

   `vevn\Scripts\activate`

3. ✅ Install django

   `pip install django`

4. ✅ Create new project

   `django-admin startproject config .`

The dot is required to create the project in current directory

5. ✅ Add your first app

   `python manage.py startapp users`

We will create an users app to manage Custom User from begging

6. ✅ To correctly integrate users ito your app we nee
   1. ✅ Create and User class from AbstractUser

   ```python
    from django.contrib.auth.models import AbstractUser

    class User(AbstractUser):
        pass
   ```

   2. ✅ Update our settings.py
      - add "users" to INSTALLED_APPS
      - Add user as AUTH_USER_MODEL `AUTH_USER_MODEL = "users.User"`

   3. ✅ Run python makemigration and migrate
      - `python manage.py makemigrations`
      - `python manage.py migrate`

7.✅ U can start app

    - via `python manage.py runserver`

8.✅ Now its time to create a plan how the models will look a like

    - You can find an entity-relationship diagram of the models in [models.mermaid](models.mermaid).

9.✅ Add new app to settings.py
   - add "flashcards" to INSTALLED_APPS

10. Create models
    - Flashcard
    - Deck
    - Flashcard user state
    - Review
