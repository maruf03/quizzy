from django.db import models
from django.contrib.auth.models import User
from quizzes.models import Quiz, Question


class Submission(models.Model):
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="submissions")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
	score = models.IntegerField(default=0)
	attempt_number = models.PositiveIntegerField(default=1)
	in_progress = models.BooleanField(default=True)
	submitted_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("quiz", "user", "attempt_number")

	def __str__(self) -> str:  # pragma: no cover
		return f"Submission {self.user_id} -> {self.quiz_id} (#{self.attempt_number})"


class QuestionAttempt(models.Model):
	submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="question_attempts")
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	selected_answer_id = models.IntegerField(null=True, blank=True)
	is_correct = models.BooleanField(default=False)
	attempt_number = models.PositiveIntegerField(default=1)
	attempted_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		indexes = [
			models.Index(fields=["submission", "question", "attempt_number"]),
		]

	def __str__(self) -> str:  # pragma: no cover
		return f"Attempt Q{self.question_id} sub {self.submission_id}"

