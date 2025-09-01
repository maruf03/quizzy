from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
	PUBLIC = "public"
	PRIVATE = "private"
	VISIBILITY_CHOICES = [(PUBLIC, "Public"), (PRIVATE, "Private")]

	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quizzes")
	created_at = models.DateTimeField(auto_now_add=True)
	is_published = models.BooleanField(default=False)
	visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default=PUBLIC)
	allow_multiple_attempts = models.BooleanField(default=False)
	max_attempts = models.PositiveIntegerField(null=True, blank=True)
	scoring_policy = models.CharField(max_length=10, default="best")

	def __str__(self) -> str:  # pragma: no cover
		return self.title


class Question(models.Model):
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
	text = models.TextField()
	allow_multiple_attempts = models.BooleanField(default=False)
	max_attempts = models.PositiveIntegerField(null=True, blank=True)

	def __str__(self) -> str:  # pragma: no cover
		return f"Q{self.pk}: {self.text[:50]}"


class Answer(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
	text = models.CharField(max_length=255)
	is_correct = models.BooleanField(default=False)

	def __str__(self) -> str:  # pragma: no cover
		return self.text


class Invitation(models.Model):
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="invitations")
	email = models.EmailField()
	invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
	accepted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("quiz", "email")

	def __str__(self) -> str:  # pragma: no cover
		return f"Invite {self.email} -> {self.quiz_id}"

