from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from apps.users.serializers import RequestPostUserStorySerializer, UserSerializer
from django.http import FileResponse, Http404, HttpResponse
from project import settings
from apps.story.models import Video
from project.auth import ApiKeyAuthentication


class UsersView(APIView):
    @extend_schema(
        tags=["Users"],
        operation_id="post_users",
        summary="Создать пользователя",
        description="Создать пользователя",
        request=RequestPostUserStorySerializer,
        responses={
            201: OpenApiResponse(
                response=UserSerializer,
            )
        },
    )
    def post(self, request: Request) -> Response:
        serializer = RequestPostUserStorySerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.create()
        print("!!user", user.id)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
