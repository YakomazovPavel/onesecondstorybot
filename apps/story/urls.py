from django.urls import path

from apps.story.views import DayStoryView, DayStoryDetailView, StoryVideoDetailView

urlpatterns = [
    path("day/", DayStoryView.as_view(), name="DayStoryView"),
    path("day/<str:id>/", DayStoryDetailView.as_view(), name="DayStoryView"),
    path("video/<str:id>/", StoryVideoDetailView.as_view(), name="DayStoryView"),
]
