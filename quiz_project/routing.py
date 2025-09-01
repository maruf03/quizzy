from django.urls import re_path
from realtime.consumers import LeaderboardConsumer

websocket_urlpatterns = [
    re_path(r"^ws/quizzes/(?P<quiz_id>\d+)/leaderboard/$", LeaderboardConsumer.as_asgi()),
]
