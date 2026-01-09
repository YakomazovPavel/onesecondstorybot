import uuid
from rest_framework import serializers
from apps.users.models import User


class RequestPostUserStorySerializer(serializers.Serializer):
    telegram_chat_id = serializers.CharField(
        required=True,
        allow_null=False,
    )
    telegram_username = serializers.CharField(
        required=True,
        allow_null=False,
    )
    telegram_photo_url = serializers.CharField(
        required=True,
        allow_null=True,
    )

    def create(self) -> User:
        user = User.objects.filter(
            telegram_chat_id=self.validated_data.get("telegram_chat_id")
        ).first()
        if user:
            return user
        user_id = str(uuid.uuid4())
        return User.objects.create(
            id=user_id,
            username=user_id,
            telegram_chat_id=self.validated_data.get("telegram_chat_id"),
            telegram_username=self.validated_data.get("telegram_username"),
            telegram_photo_url=self.validated_data.get("telegram_photo_url"),
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "telegram_chat_id",
            "telegram_username",
            "telegram_photo_url",
        ]
