from django.urls import path

from apps.story.views import (
    DayStoryView,
    DayStoryDetailView,
    MonthStoryView,
    MonthStoryDetailView,
    YearStoryView,
    YearStoryDetailView,
)

urlpatterns = [
    path("day/", DayStoryView.as_view()),
    path("month/", MonthStoryView.as_view()),
    path("year/", YearStoryView.as_view()),
    path("day/<str:id>/", DayStoryDetailView.as_view()),
    path("month/<str:id>/", MonthStoryDetailView.as_view()),
    path("year/<str:id>/", YearStoryDetailView.as_view()),
]
