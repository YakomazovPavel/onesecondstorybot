from rest_framework import serializers
from apps.story.models import DayStory, MonthStory, Video
from apps.users.models import User
from project import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
from pathlib import Path
import ffmpeg
import os


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
        path_output = f"{settings.MEDIA_ROOT}/{video_id}.cnv.mp4"
        path_cut_output = f"{settings.MEDIA_ROOT}/{video_id}.cut.mp4"

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
        finally:
            os.system(f"rm {path_input}")

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
        finally:
            os.system(f"rm {path_output}")

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


class RequestPostMonthStorySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    month = serializers.IntegerField(
        required=True,
        allow_null=False,
    )

    def create(self) -> DayStory:

        user: User = self.context.get("request").user

        video_ids = (
            DayStory.objects.filter(
                year=self.validated_data.get("year"),
                month=self.validated_data.get("month"),
                user=user,
            )
            .order_by("day")
            .values_list("video_id", flat=True)
        )

        videos_paths = Video.objects.filter(id__in=video_ids).values_list(
            "path", flat=True
        )

        if not videos_paths:
            raise serializers.ValidationError("Отсутствуют видео за этот месяц")

        # Создать временный файл txt
        new_uuid = uuid.uuid4()

        text = "\n".join([f"file '{path}'" for path in videos_paths])

        print(f"text\n{text}")

        temp_path_to_txt = f"{settings.MEDIA_ROOT}/{new_uuid}.concat.txt"
        path_output = f"{settings.MEDIA_ROOT}/{new_uuid}.concat.mp4"

        with open(temp_path_to_txt, "wb") as f:
            f.write(text.encode("utf-8"))
            # f.close()

        try:
            cmd = (
                f"ffmpeg -f concat -safe 0 -i {temp_path_to_txt} -c copy {path_output}"
            )
            print(f"!cmd\n{cmd}")
            exit_code = os.system(cmd)
            print("Exit Code:", exit_code)
            if exit_code != 0:
                raise RuntimeError(f"Не удалось склеить видео {exit_code}")
        except Exception as e:
            print("FFmpeg Concat Error:", e)
            raise serializers.ValidationError("Не удалось склеить видео")
        finally:
            os.system(f"rm {temp_path_to_txt}")

        video: Video = Video.objects.create(
            id=new_uuid,
            user=user,
            path=path_output,
            content_type="video/mp4",
        )

        # Удалить предыдущую историю за этот месяц
        MonthStory.objects.filter(
            month=self.validated_data.get("month"),
            year=self.validated_data.get("year"),
            user=user,
        ).delete()

        return MonthStory.objects.create(
            month=self.validated_data.get("month"),
            year=self.validated_data.get("year"),
            video=video,
            user=user,
        )
