from rest_framework import serializers

from quizzes.models import Quiz, Question, Answer, Invitation
from submissions.models import Submission


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "answers"]


class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "visibility",
            "is_published",
            "creator",
            "created_at",
        ]


class QuizDetailSerializer(QuizListSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta(QuizListSerializer.Meta):
        fields = QuizListSerializer.Meta.fields + ["questions"]


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["id", "email", "accepted", "created_at"]


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            "id",
            "quiz",
            "user",
            "score",
            "attempt_number",
            "in_progress",
            "submitted_at",
        ]
        read_only_fields = ["user", "score", "in_progress", "submitted_at"]


class SubmitPayloadSerializer(serializers.Serializer):
    # Mapping of question_id -> answer_id (or None)
    answers = serializers.DictField(child=serializers.IntegerField(allow_null=True), allow_empty=False)
