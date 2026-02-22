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

from apps.story.models import DayStory, Video, MonthStory, YearStory
from apps.story.serializers import (
    DayStorySerializer,
    MonthStorySerializer,
    RequestPostDayStorySerializer,
    RequestPostMonthStorySerializer,
    RequestPostYearStorySerializer,
    YearStorySerializer,
)
from project.auth import ApiKeyAuthentication
from rest_framework.exceptions import NotFound


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
            data=request.data,
            context={"request": request},
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
                required=False,
            ),
            OpenApiParameter(
                name="month",
                description="Месяц",
                type=int,
                required=False,
            ),
            OpenApiParameter(
                name="day",
                description="День",
                type=int,
                required=False,
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=DayStorySerializer(many=True),
            )
        },
    )
    def get(self, request: Request):
        print("!get_day_story")
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
    authentication_classes = [ApiKeyAuthentication]

    @extend_schema(
        operation_id="get_video",
        summary="Получить видео",
        description="Получить видео",
        tags=["Video"],
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="Видео",
            )
        },
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


class MonthStoryView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    @extend_schema(
        operation_id="post_month_story",
        summary="Сгенерировать видео за месяц",
        description="Сгенерировать видео за месяц",
        tags=["Story Month"],
        request=RequestPostMonthStorySerializer,
        responses={
            201: OpenApiResponse(
                response=MonthStorySerializer,
            )
        },
    )
    def post(self, request: Request) -> Response:
        serializer = RequestPostMonthStorySerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        month_story: MonthStory = serializer.create()

        return Response(
            MonthStorySerializer(month_story).data,
            status=status.HTTP_201_CREATED,
        )


class MonthStoryDetailView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    @property
    def month_story(self) -> MonthStory:
        month_story = MonthStory.objects.filter(
            id=self.kwargs.get("id"),
            user=self.request.user,
        ).first()
        if not month_story:
            raise NotFound
        return month_story

    @extend_schema(
        operation_id="get_month_story",
        summary="Получить историю за месяц",
        description="Получить историю за месяц",
        tags=["Story Month"],
        parameters=[
            OpenApiParameter(
                "id",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="ID истории месяца",
                required=True,
            )
        ],
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="Видео",
            )
        },
    )
    def get(self, request: Request, id: str) -> Response:

        return Response(
            MonthStorySerializer(self.month_story).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="delete_month_story",
        summary="Удалить историю за месяц",
        description="Удалить историю за месяц",
        tags=["Story Month"],
        parameters=[
            OpenApiParameter(
                "id",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="ID истории месяца",
                required=True,
            )
        ],
        request=None,
        responses={204: None},
    )
    def delete(self, request: Request, id) -> Response:
        month_story = self.month_story
        os.system(f"rm {month_story.video.path}")
        month_story.video.delete()
        month_story.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class YearStoryView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    @extend_schema(
        operation_id="post_year_story",
        summary="Сгенерировать историю за год",
        description="Сгенерировать историю за год",
        tags=["Story Year"],
        request=RequestPostYearStorySerializer,
        responses={
            201: OpenApiResponse(
                response=YearStorySerializer,
            )
        },
    )
    def post(self, request: Request) -> Response:
        serializer = RequestPostYearStorySerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        year_story: YearStory = serializer.create()

        return Response(
            YearStorySerializer(year_story).data,
            status=status.HTTP_201_CREATED,
        )


class YearStoryDetailView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    @property
    def year_story(self) -> YearStory:
        year_story = YearStory.objects.filter(
            id=self.kwargs.get("id"),
            user=self.request.user,
        ).first()
        if not year_story:
            raise NotFound
        return year_story

    @extend_schema(
        operation_id="get_year_story",
        summary="Получить историю за год",
        description="Получить историю за год",
        tags=["Story Year"],
        parameters=[
            OpenApiParameter(
                "id",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="ID истории года",
                required=True,
            )
        ],
        request=None,
        responses={
            200: OpenApiResponse(
                response=YearStorySerializer,
            )
        },
    )
    def get(self, request: Request, id: str) -> Response:
        return Response(
            MonthStorySerializer(self.year_story).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="delete_year_story",
        summary="Удалить историю за год",
        description="Удалить историю за год",
        tags=["Story Year"],
        parameters=[
            OpenApiParameter(
                "id",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="ID истории года",
                required=True,
            )
        ],
        request=None,
        responses={204: None},
    )
    def delete(self, request: Request, id) -> Response:
        year_story = self.year_story
        os.system(f"rm {year_story.video.path}")
        year_story.video.delete()
        year_story.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
