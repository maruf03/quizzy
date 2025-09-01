from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistrationForm
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
