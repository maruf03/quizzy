from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from quizzes.models import Quiz, Question, Answer
from quizzes.services import invite_email, accept_invite
from submissions.models import Submission, QuestionAttempt
from .serializers import (
	QuizListSerializer,
	QuizDetailSerializer,
	SubmissionSerializer,
	SubmitPayloadSerializer,
	InvitationSerializer,
)
from .permissions import CanViewQuiz, IsCreatorOrReadOnly


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Quiz.objects.all().select_related("creator")
	permission_classes = [AllowAny]

	def get_serializer_class(self):
		if self.action == "retrieve":
			return QuizDetailSerializer
		return QuizListSerializer

	def get_queryset(self):
		qs = super().get_queryset()
		# Only list public, published quizzes
		if self.action == "list":
			return qs.filter(is_published=True, visibility=Quiz.PUBLIC).order_by("-created_at")
		return qs

	def retrieve(self, request, *args, **kwargs):
		obj = self.get_object()
		# Enforce visibility rules using permission
		self.check_object_permissions(request, obj)
		serializer = self.get_serializer(obj)
		return Response(serializer.data)

	def get_permissions(self):
		if self.action in {"retrieve"}:
			return [CanViewQuiz()]
		return super().get_permissions()

	@action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
	def submit(self, request, pk=None):
		quiz = self.get_object()
		# Enforce the same view permission for taking the quiz
		CanViewQuiz().has_object_permission(request, self, quiz) or self.permission_denied(request)

		payload = SubmitPayloadSerializer(data=request.data)
		payload.is_valid(raise_exception=True)
		answers_map = payload.validated_data["answers"]

		with transaction.atomic():
			submission, _ = Submission.objects.get_or_create(
				quiz=quiz, user=request.user, attempt_number=1, defaults={"in_progress": True}
			)

			questions = Question.objects.filter(quiz=quiz).prefetch_related("answers")
			for q in questions:
				selected_id = answers_map.get(str(q.id)) or answers_map.get(q.id)
				is_correct = False
				if selected_id:
					is_correct = Answer.objects.filter(pk=selected_id, question=q, is_correct=True).exists()
				QuestionAttempt.objects.create(
					submission=submission,
					question=q,
					selected_answer_id=selected_id,
					is_correct=is_correct,
					attempt_number=1,
				)

			Submission.objects.filter(pk=submission.pk).update(in_progress=False)

		return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
	def invite(self, request, pk=None):
		quiz = self.get_object()
		email = request.data.get("email", "").strip()
		invite = invite_email(request.user, quiz, email)
		return Response(InvitationSerializer(invite).data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
	def accept(self, request, pk=None):
		quiz = self.get_object()
		accept_invite(request.user, quiz)
		return Response({"accepted": True})


class SubmissionViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
	serializer_class = SubmissionSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return Submission.objects.filter(user=self.request.user).select_related("quiz")

