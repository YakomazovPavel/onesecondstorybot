from django.db import models
from apps.users.models import User
import uuid


class DayStory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    day = models.PositiveSmallIntegerField()

    video = models.ForeignKey("Video", models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)

    class Meta:
        db_table = "day_story"


class MonthStory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    video = models.ForeignKey("Video", models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)

    class Meta:
        db_table = "month_story"


class YearStory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    year = models.PositiveSmallIntegerField()
    video = models.ForeignKey("Video", models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)

    class Meta:
        db_table = "year_story"


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    path = models.CharField(null=True)
    content_type = models.CharField(null=True)
    user = models.ForeignKey(User, models.CASCADE)

    class Meta:
        db_table = "video"
