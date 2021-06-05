from django.urls import path
from . import views
urlpatterns = [
  path("register/", view=views.register, name="register"),
  path("modifyAccount/", views.modify_user, name="modifyAccount"),
]