from django.urls import path
from .views import (
    QuizListView,
    QuizDetailView,
    TakeQuizView,
    SubmissionResultsView,
    InviteView,
    AcceptInviteView,
    DeclineInviteView,
    MyQuizListView,
    QuizCreateView,
    QuizUpdateView,
    QuizDeleteView,
    QuestionListView,
    QuestionEditView,
    
    # Leaderboard full view
    QuizLeaderboardView,
    InvitationsListView,
)


app_name = "quizzes"

urlpatterns = [
    path("", QuizListView.as_view(), name="list"),
    path("<int:pk>/", QuizDetailView.as_view(), name="detail"),
    path("<int:pk>/take/", TakeQuizView.as_view(), name="take"),
    path("submissions/<int:pk>/", SubmissionResultsView.as_view(), name="results"),
    path("<int:pk>/invite/", InviteView.as_view(), name="invite"),
    path("<int:pk>/accept/", AcceptInviteView.as_view(), name="accept-invite"),
    path("<int:pk>/decline/", DeclineInviteView.as_view(), name="decline-invite"),
    # Creator CRUD
    path("my/", MyQuizListView.as_view(), name="my-list"),
    path("my/new/", QuizCreateView.as_view(), name="create"),
    path("my/<int:pk>/edit/", QuizUpdateView.as_view(), name="edit"),
    path("my/<int:pk>/delete/", QuizDeleteView.as_view(), name="delete"),
    path("my/<int:pk>/questions/", QuestionListView.as_view(), name="questions"),
    path("my/<int:pk>/questions/new/", QuestionEditView.as_view(), name="question-new"),
    path("my/<int:pk>/questions/<int:qid>/edit/", QuestionEditView.as_view(), name="question-edit"),
    # Full leaderboard
    path("<int:pk>/leaderboard/", QuizLeaderboardView.as_view(), name="leaderboard"),
    path("invitations/", InvitationsListView.as_view(), name="invitations"),
]
