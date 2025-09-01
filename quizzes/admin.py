from django.contrib import admin
from .models import Quiz, Question, Answer, Invitation


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
	list_display = ("title", "creator", "is_published", "visibility", "scoring_policy", "created_at")
	list_filter = ("is_published", "visibility", "scoring_policy", "created_at")
	search_fields = ("title", "description", "creator__username", "creator__email")


class AnswerInline(admin.TabularInline):
	model = Answer
	extra = 1


class QuestionInline(admin.StackedInline):
	model = Question
	extra = 1
	show_change_link = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ("id", "quiz", "text")
	search_fields = ("text", "quiz__title")
	inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
	list_display = ("id", "question", "text", "is_correct")
	list_filter = ("is_correct",)
	search_fields = ("text", "question__text")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
	list_display = ("quiz", "email", "invited_by", "accepted", "created_at")
	list_filter = ("accepted", "created_at")
	search_fields = ("email", "quiz__title", "invited_by__username")
