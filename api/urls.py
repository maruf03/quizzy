from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, SubmissionViewSet


router = DefaultRouter()
router.register(r"quizzes", QuizViewSet, basename="quiz")
router.register(r"submissions", SubmissionViewSet, basename="submission")

urlpatterns = router.urls
