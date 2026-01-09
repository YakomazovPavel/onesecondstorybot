import os
from django.http import FileResponse, HttpResponseNotFound
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.story.models import DayStory, Video
from apps.story.serializers import DayStorySerializer, RequestPostDayStorySerializer
from project import settings
from project.auth import ApiKeyAuthentication


class DayStoryView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = RequestPostDayStorySerializer
    authentication_classes = [ApiKeyAuthentication]

    @extend_schema(
        tags=["Story Day"],
        operation_id="post_day_story",
        summary="Создать историю дня",
        description="Создать историю дня",
        request=RequestPostDayStorySerializer,
        responses={
            201: OpenApiResponse(
                response=DayStorySerializer,
            )
        },
    )
    def post(self, request: Request) -> Response:
        serializer = RequestPostDayStorySerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        day_story = serializer.create()
        return Response(
            DayStorySerializer(day_story).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Story Day"],
        operation_id="get_day_story",
        summary="Получить истории",
        description="Получить истории",
        parameters=[
            OpenApiParameter(
                name="year",
                description="Год",
                type=int,
            ),
            OpenApiParameter(
                name="month",
                description="Месяц",
                type=int,
            ),
            OpenApiParameter(
                name="day",
                description="День",
                type=int,
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=DayStorySerializer(many=True),
            )
        },
    )
    def get(self, request: Request):
        q = DayStory.objects.filter(user=request.user)

        year = request.query_params.get("year")
        month = request.query_params.get("month")
        day = request.query_params.get("day")

        if year:
            q = q.filter(year=year)
        if month:
            q = q.filter(month=month)
        if day:
            q = q.filter(day=day)

        return Response(
            DayStorySerializer(q, many=True).data,
        )


class DayStoryDetailView(APIView):
    serializer_class = RequestPostDayStorySerializer

    authentication_classes = [ApiKeyAuthentication]

    @extend_schema(
        tags=["Story Day"],
        operation_id="delete_day_story",
        summary="Удалить историю дня",
        description="Удалить историю дня",
        parameters=[
            OpenApiParameter(
                "id",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="ID Story Day",
                required=True,
            )
        ],
        request=None,
        responses={204: None},
    )
    def delete(self, request: Request, id: str) -> Response:
        day_story: DayStory = DayStory.objects.filter(id=id, user=request.user).first()
        os.system(f"rm {day_story.video.path}")
        day_story.video.delete()
        return Response(True)


class StoryVideoDetailView(APIView):
    serializer_class = RequestPostDayStorySerializer
    authentication_classes = [ApiKeyAuthentication]

    @extend_schema(
        operation_id="get_video_story",
        summary="Получить видео",
        description="Получить видео",
        tags=["Story Day"],
    )
    def get(self, request: Request, id: str):
        video: Video = Video.objects.filter(id=id, user=request.user).first()
        if video:
            return FileResponse(
                open(f"{video.path}", "rb"),
                filename=video.path,
                content_type=video.content_type,
                as_attachment=True,
            )
        else:
            return HttpResponseNotFound()
