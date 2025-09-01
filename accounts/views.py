from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .forms import RegistrationForm, ProfileForm
from django.urls import reverse_lazy
from django.views.generic import FormView

# Create your views here.
class RegisterView(FormView):
	template_name = "registration/register.html"
	form_class = RegistrationForm
	success_url = reverse_lazy("home")

	def form_valid(self, form):
		user = form.save()
		# Explicit backend required because multiple authentication backends are configured
		login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
		return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, FormView):
	template_name = "accounts/profile_edit.html"
	form_class = ProfileForm

	def get_initial(self):
		u = self.request.user
		return {"first_name": u.first_name, "last_name": u.last_name}

	def form_valid(self, form):
		u = self.request.user
		u.first_name = form.cleaned_data["first_name"]
		u.last_name = form.cleaned_data["last_name"]
		u.save(update_fields=["first_name", "last_name"])
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("accounts:profile")
