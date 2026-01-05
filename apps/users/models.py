from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_first_start = models.BooleanField(default=True)

    class Meta:
        db_table = "users"
