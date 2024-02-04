from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api import views

router = DefaultRouter()
router.register(r"notes", views.NoteViewSet, basename="note")

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("bepa-callback/", views.BepaCallbackView.as_view(), name="bepa-callback"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("verify-token/", views.VerifyTokenView.as_view(), name="verify-token"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("my-team/", views.MyTeamView.as_view(), name="my-team"),
    path("users/", views.UsersView.as_view(), name="users"),
    path("", include(router.urls)),
]

if settings.SIGNUP_DISABLED != "true":
    urlpatterns.append(path("signup/", views.SignupView.as_view(), name="signup"))
