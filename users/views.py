from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls.base import reverse
from .forms import CustomUserCreationForm, CustomUserCreationForm2
from business.models import Customer

# Create your views here.
def register(request):
  if request.method == "GET":
    context = {
      "form": CustomUserCreationForm,
    }
    return render(request, "register.html", context)
  elif request.method == "POST":
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      customer = Customer()
      customer.user = user
      customer.phone = form.cleaned_data["phone"]
      customer.save()
      login(request, user)
      return redirect(reverse("home"))

def modify_user(request):
  if request.method == "POST":
    form = CustomUserCreationForm2(request.POST)
    if form.is_valid():
      user = User.objects.get(pk=request.user.pk)
      print(user.has_perm('auth.change_user'))
      user.first_name = form.cleaned_data["first_name"]
      user.last_name = form.cleaned_data["last_name"]
      user.email = form.cleaned_data["email"]
      user.save()
      customer = user.customer_info
      customer.phone = form.cleaned_data["phone"]
      customer.save()
    return redirect(reverse("myAccount"))