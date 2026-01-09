from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication
from django.contrib.auth import get_user_model

from rest_framework.request import Request
from rest_framework.exceptions import AuthenticationFailed


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):  # noqa
        auth_header = request.headers.get("Authorization")
        user = get_user_model().objects.filter(id=auth_header).first()
        if not user:
            raise AuthenticationFailed("API ключ не найден")
        return user, None


class ApiKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = ApiKeyAuthentication
    name = "1. ApiKeyAuthentication"

    def get_security_definition(self, auto_schema):  # noqa
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Аутентификация с использованием `API KEY`",
        }
