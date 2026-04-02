from django.urls import path

from .views import ChangePasswordView, ProfileView, RegisterView

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]
