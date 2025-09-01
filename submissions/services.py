from collections import defaultdict
from django.db.models import Prefetch

from .models import Submission, QuestionAttempt
from .strategies import get_strategy


def recompute_score(submission: Submission) -> int:
    """Recompute total score for a submission.

    Strategy is applied per-question on that submission's attempts,
    and the total is the sum across all questions.
    """
    # Gather attempts per question for this submission, ordered by attempt_number
    attempts = (
        QuestionAttempt.objects.filter(submission=submission)
        .select_related("question")
        .order_by("question_id", "attempt_number", "attempted_at", "id")
    )

    per_question = defaultdict(list)
    for a in attempts:
        per_question[a.question_id].append(a)

    strategy = get_strategy(submission.quiz)
    total = 0
    for _, q_attempts in per_question.items():
        total += strategy.compute(q_attempts)

    # Update and save only if changed to avoid unnecessary writes
    if submission.score != total:
        Submission.objects.filter(pk=submission.pk).update(score=total)
        submission.score = total
    return total


def remaining_attempts(user, quiz_id) -> int:
    """Compute remaining attempts for a user on a quiz (quiz-level).

    If the quiz does not allow multiple attempts, remaining is 1 if no submission exists, else 0.
    If allows multiple attempts and max_attempts is set, remaining = max_attempts - attempts_made.
    If max_attempts is not set, treat as unlimited (large number); here we return 999999.
    """
    from quizzes.models import Quiz  # local import to avoid circulars

    quiz = Quiz.objects.get(pk=quiz_id)
    attempts_made = Submission.objects.filter(quiz_id=quiz_id, user=user).count()

    if not quiz.allow_multiple_attempts:
        return 0 if attempts_made > 0 else 1

    if quiz.max_attempts is not None:
        return max(0, quiz.max_attempts - attempts_made)

    return 999_999
