from django.urls import path

from apps.users.views import UsersView

urlpatterns = [
    path("", UsersView.as_view(), name="UsersView"),
]
