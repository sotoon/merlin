from django.conf import settings
from django.urls import include, path
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api import views

router = routers.DefaultRouter()
router.register(r"notes", views.NoteViewSet, basename="note")

feedbacks_router = routers.NestedDefaultRouter(router, r"notes", lookup="note")
feedbacks_router.register(r"feedbacks", views.FeedbackViewSet, basename="feedbacks")

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("bepa-callback/", views.BepaCallbackView.as_view(), name="bepa-callback"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("verify-token/", views.VerifyTokenView.as_view(), name="verify-token"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("my-team/", views.MyTeamView.as_view(), name="my-team"),
    path("users/", views.UsersView.as_view(), name="users"),
    path("templates/", views.TemplatesView.as_view(), name="templates"),
    path("", include(router.urls)),
    path("", include(feedbacks_router.urls)),
]

if settings.SIGNUP_DISABLED != "true":
    urlpatterns.append(path("signup/", views.SignupView.as_view(), name="signup"))
