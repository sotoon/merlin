from django.conf import settings
from django.urls import include, path
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api import views

# ─── Top-level router ────────────────────────────────────────────────────────────
router = routers.DefaultRouter()
router.register(r"notes", views.NoteViewSet, basename="note")
router.register(r"my-team", views.MyTeamViewSet, basename="my-team")

# One on one related
router.register(r"my-one-on-ones", views.MyOneOnOneViewSet, basename="my-one-on-ones")

# ─── Nested under my-team for leaders ─────────────────────────────────────────────
team_router = routers.NestedDefaultRouter(router, r"my-team", lookup="member")
team_router.register(r"one-on-ones", views.OneOnOneViewSet, basename="member-oneonones")

# ─── Nested comments & summaries ─────────────────────────────────────────────────
comments_router = routers.NestedDefaultRouter(router, r"notes", lookup="note")
comments_router.register(r"comments", views.CommentViewSet, basename="comments")

summaries_router = routers.NestedDefaultRouter(router, r"notes", lookup="note")
summaries_router.register(r"summaries", views.SummaryViewSet, basename="summaries")

# ─── Forms router ────────────────────────────────────────────────────────────────
forms_router = routers.DefaultRouter()
forms_router.register(r"forms", views.FormViewSet, basename="forms")

# ─── Nested feedback and routers ─────────────────────────────────────────────
router.register(r"feedback-forms",    views.FeedbackFormViewSet,    basename="feedback-forms")
router.register(r"feedback-requests", views.FeedbackRequestViewSet, basename="feedback-requests")
router.register(r"feedback-entries",  views.FeedbackEntryViewSet,   basename="feedback-entries")

# ─── URL PATTERNS ────────────────────────────────────────────────────────────────
urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("bepa-callback/", views.BepaCallbackView.as_view(), name="bepa-callback"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("verify-token/", views.VerifyTokenView.as_view(), name="verify-token"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("users/", views.UsersView.as_view(), name="users"),
    path("templates/", views.TemplatesView.as_view(), name="templates"),
    path("value-tags/", views.ValueTagListView.as_view(), name="value-tags"),
    path("", include(router.urls)),
    path("", include(comments_router.urls)),
    path("", include(summaries_router.urls)),
    path("", include(forms_router.urls)),
    path("", include(team_router.urls)),
]

if settings.SIGNUP_DISABLED != "true":
    urlpatterns.append(path("signup/", views.SignupView.as_view(), name="signup"))
