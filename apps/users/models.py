from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    telegram_chat_id = models.CharField(null=True)
    telegram_username = models.CharField(null=True)
    telegram_photo_url = models.CharField(null=True)

    class Meta:
        db_table = "users"
