from rest_framework import serializers
from apps.story.models import DayStory, Video
from apps.users.models import User
from project import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
from pathlib import Path
import ffmpeg


class RequestPostDayStorySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    month = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    day = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    file = serializers.FileField(
        required=True,
        allow_empty_file=False,
        allow_null=False,
    )

    def create(self) -> DayStory:
        file: InMemoryUploadedFile = self.validated_data.get("file")
        print("!file", file)

        user: User = self.context.get("request").user
        print("!user", user.id)
        video_id = str(uuid.uuid4())

        path_input = f"{settings.MEDIA_ROOT}/{video_id}{Path(file.name).suffixes[-1]}"
        path_output = f"{settings.MEDIA_ROOT}/{video_id}.webm"
        path_cut_output = f"{settings.MEDIA_ROOT}/{video_id}.cut.webm"

        video: Video = Video.objects.create(
            id=video_id,
            user=user,
            path=path_cut_output,
            content_type=file.content_type,
        )

        with open(path_input, "wb") as f:
            f.write(file.read())
        try:
            (
                ffmpeg.input(path_input).output(path_output).run()
                # .overwrite_output()  # Overwrite output file if it exists
            )
        except ffmpeg.Error as e:
            print("FFmpeg Convert Error:", e)
            raise serializers.ValidationError("Ошибка конвертации файла")

        try:
            (
                ffmpeg.input(path_output)
                .output(path_cut_output, **{"ss": "00:00:00", "to": "00:00:01"})
                .run()
                # .overwrite_output()
            )
        except ffmpeg.Error as e:
            print("FFmpeg Cut Error:", e)
            raise serializers.ValidationError("Ошибка обрезания файла")

        return DayStory.objects.create(
            year=self.validated_data.get("year"),
            month=self.validated_data.get("month"),
            day=self.validated_data.get("day"),
            video=video,
            user=user,
        )


class DayStorySerializer(serializers.ModelSerializer):
    video_id = serializers.SerializerMethodField(
        source="get_video_id",
    )

    def get_video_id(self, instance: DayStory) -> str:
        return instance.video.id

    class Meta:
        model = DayStory
        fields = [
            "id",
            "year",
            "month",
            "day",
            "video_id",
        ]
