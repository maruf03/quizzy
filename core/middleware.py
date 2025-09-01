from django.http import HttpResponseForbidden


class AttemptGuardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None
        # Target only the quiz-start endpoint pattern
        if request.path.endswith("/start/"):
            quiz_id = view_kwargs.get("pk")
            if not quiz_id:
                return None
            # Owner cannot attempt their own quiz
            from quizzes.models import Quiz

            try:
                quiz = Quiz.objects.only("id", "creator_id").get(pk=quiz_id)
            except Quiz.DoesNotExist:
                return None

            if quiz.creator_id == request.user.id:
                return HttpResponseForbidden("Owners cannot attempt their own quizzes")

            # Enforce remaining attempts
            from submissions.services import remaining_attempts

            if remaining_attempts(request.user, quiz_id) <= 0:
                return HttpResponseForbidden("No attempts left")
        return None
