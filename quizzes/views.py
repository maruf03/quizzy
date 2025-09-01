from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, TemplateView, FormView, View
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Quiz, Question, Answer
from .services import is_invited, invite_email, accept_invite, decline_invite
from submissions.models import Submission, QuestionAttempt
from .forms import QuestionForm, AnswerFormSet
from quizzes.models import Invitation


@login_required
def start_quiz(request, pk):
	# Minimal stub used for middleware tests; real logic added in later steps
	return HttpResponse(f"Started quiz {pk}")


@method_decorator(cache_page(60), name="dispatch")
class QuizListView(ListView):
	model = Quiz
	template_name = "quizzes/quiz_list.html"
	context_object_name = "quizzes"

	def get_queryset(self):
		qs = Quiz.objects.filter(is_published=True)
		# For now, only show public quizzes in list to keep it simple
		return qs.filter(visibility=Quiz.PUBLIC).order_by("-created_at")


class QuizDetailView(DetailView):
	model = Quiz
	template_name = "quizzes/quiz_detail.html"
	context_object_name = "quiz"

	def get_object(self, queryset=None):
		obj = super().get_object(queryset)
		user = self.request.user
		if obj.is_published:
			return obj
		# Allow creator to view drafts
		if user.is_authenticated and obj.creator_id == user.id:
			return obj
		raise Http404()


class TakeQuizView(LoginRequiredMixin, TemplateView):
	template_name = "quizzes/quiz_take.html"

	def dispatch(self, request, *args, **kwargs):
		self.quiz = get_object_or_404(Quiz, pk=kwargs["pk"])
		if not self.quiz.is_published:
			raise Http404()
		# Enforce private quiz invitation
		if self.quiz.visibility == Quiz.PRIVATE and not is_invited(request.user, self.quiz):
			raise Http404()
		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		questions = Question.objects.filter(quiz=self.quiz).prefetch_related("answers")
		ctx.update({
			"quiz": self.quiz,
			"questions": questions,
		})
		return ctx

	def post(self, request, *args, **kwargs):
		# Create or reuse submission (attempt 1 for now)
		submission, _ = Submission.objects.get_or_create(
			quiz=self.quiz, user=request.user, attempt_number=1,
			defaults={"in_progress": True},
		)

		questions = Question.objects.filter(quiz=self.quiz).prefetch_related("answers")
		for q in questions:
			key = f"answer_{q.id}"
			if key not in request.POST:
				continue
			try:
				selected_id = int(request.POST[key])
			except ValueError:
				selected_id = None
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

		# Mark submission complete
		Submission.objects.filter(pk=submission.pk).update(in_progress=False)
		submission.in_progress = False
		return redirect(reverse("quizzes:results", kwargs={"pk": submission.pk}))


class SubmissionResultsView(LoginRequiredMixin, DetailView):
	model = Submission
	template_name = "quizzes/quiz_results.html"
	context_object_name = "submission"

	def get_queryset(self):
		# A user can only view their own submissions
		return Submission.objects.filter(user=self.request.user).select_related("quiz")


class InviteView(LoginRequiredMixin, FormView):
	template_name = "quizzes/invite.html"

	def get_form(self):
		# Minimal form-less implementation using POST field 'email'
		class F:
			cleaned_data = {}
			def is_valid(self_inner):
				return True
		return F()

	def form_valid(self, form):
		quiz = get_object_or_404(Quiz, pk=self.kwargs["pk"]) 
		email = self.request.POST.get("email", "").strip()
		if email:
			invite_email(self.request.user, quiz, email)
		return redirect(reverse("quizzes:detail", kwargs={"pk": quiz.pk}))


class AcceptInviteView(LoginRequiredMixin, View):
	def post(self, request, *args, **kwargs):
		quiz = get_object_or_404(Quiz, pk=kwargs["pk"]) 
		accept_invite(request.user, quiz)
		messages.success(request, f"Invitation accepted for '{quiz.title}'.")
		return redirect(reverse("quizzes:detail", kwargs={"pk": quiz.pk}))


class DeclineInviteView(LoginRequiredMixin, View):
	def post(self, request, *args, **kwargs):
		quiz = get_object_or_404(Quiz, pk=kwargs["pk"]) 
		decline_invite(request.user, quiz)
		messages.info(request, f"Invitation declined for '{quiz.title}'.")
		return redirect(reverse("quizzes:invitations"))


class MyQuizListView(LoginRequiredMixin, ListView):
	template_name = "quizzes/my_quizzes_list.html"
	model = Quiz
	context_object_name = "quizzes"

	def get_queryset(self):
		return Quiz.objects.filter(creator=self.request.user).order_by("-created_at")


class OwnerRequiredMixin(LoginRequiredMixin):
	def dispatch(self, request, *args, **kwargs):
		if hasattr(self, 'object') and self.object:
			if self.object.creator_id != request.user.id:
				raise Http404()
		return super().dispatch(request, *args, **kwargs)


class QuizCreateView(LoginRequiredMixin, CreateView):
	model = Quiz
	fields = [
		"title", "description", "is_published", "visibility",
		"allow_multiple_attempts", "max_attempts", "scoring_policy",
	]
	template_name = "quizzes/quiz_form.html"

	def form_valid(self, form):
		form.instance.creator = self.request.user
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("quizzes:my-list")


class QuizUpdateView(LoginRequiredMixin, UpdateView):
	model = Quiz
	fields = [
		"title", "description", "is_published", "visibility",
		"allow_multiple_attempts", "max_attempts", "scoring_policy",
	]
	template_name = "quizzes/quiz_form.html"

	def get_queryset(self):
		return Quiz.objects.filter(creator=self.request.user)

	def get_success_url(self):
		return reverse("quizzes:my-list")


class QuizDeleteView(LoginRequiredMixin, DeleteView):
	model = Quiz
	template_name = "quizzes/quiz_confirm_delete.html"

	def get_queryset(self):
		return Quiz.objects.filter(creator=self.request.user)

	def get_success_url(self):
		return reverse("quizzes:my-list")


class QuestionListView(LoginRequiredMixin, ListView):
	template_name = "quizzes/questions_list.html"
	model = Question
	context_object_name = "questions"

	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return self.handle_no_permission()
		self.quiz = get_object_or_404(Quiz, pk=kwargs["pk"], creator=request.user)
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self):
		return Question.objects.filter(quiz=self.quiz)

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["quiz"] = self.quiz
		return ctx


class QuestionEditView(LoginRequiredMixin, TemplateView):
	template_name = "quizzes/question_form.html"

	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return self.handle_no_permission()
		self.quiz = get_object_or_404(Quiz, pk=kwargs["pk"], creator=request.user)
		self.question = None
		qid = kwargs.get("qid")
		if qid:
			self.question = get_object_or_404(Question, pk=qid, quiz=self.quiz)
		return super().dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		form = QuestionForm(instance=self.question)
		formset = AnswerFormSet(instance=self.question)
		return self.render_to_response({"form": form, "formset": formset, "quiz": self.quiz, "question": self.question})

	def post(self, request, *args, **kwargs):
		form = QuestionForm(request.POST, instance=self.question)
		if self.question is None:
			# Create with quiz
			if form.is_valid():
				q = form.save(commit=False)
				q.quiz = self.quiz
				q.save()
				formset = AnswerFormSet(request.POST, instance=q)
				if formset.is_valid():
					formset.save()
					return redirect(reverse("quizzes:questions", kwargs={"pk": self.quiz.pk}))
				else:
					return self.render_to_response({"form": form, "formset": formset, "quiz": self.quiz, "question": q})
			else:
				formset = AnswerFormSet(request.POST)
				return self.render_to_response({"form": form, "formset": formset, "quiz": self.quiz, "question": None})
		else:
			formset = AnswerFormSet(request.POST, instance=self.question)
			if form.is_valid() and formset.is_valid():
				form.save()
				formset.save()
				return redirect(reverse("quizzes:questions", kwargs={"pk": self.quiz.pk}))
			return self.render_to_response({"form": form, "formset": formset, "quiz": self.quiz, "question": self.question})


class QuizLeaderboardView(DetailView):
	"""Full leaderboard page (top 100 submissions)."""
	model = Quiz
	template_name = "quizzes/leaderboard_full.html"
	context_object_name = "quiz"

	def get_object(self, queryset=None):  # Reuse draft visibility rules
		obj = super().get_object(queryset)
		user = self.request.user
		if obj.is_published:
			return obj
		if user.is_authenticated and obj.creator_id == user.id:
			return obj
		raise Http404()

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		entries = (Submission.objects.filter(quiz=self.object, in_progress=False)
			.select_related("user")
			.order_by('-score', 'submitted_at')[:100])
		ctx["entries"] = entries
		return ctx


class InvitationsListView(LoginRequiredMixin, ListView):
	template_name = "quizzes/invitations_list.html"
	context_object_name = "invitations"

	def get_queryset(self):
		user = self.request.user
		# Invitations where user is the intended recipient by email or ones they sent
		return Invitation.objects.filter(email=user.email).order_by('-created_at')
