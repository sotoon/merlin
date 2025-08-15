from django.conf import settings
from django.urls import include, path
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api import views
from api.views import UserTimelineView, PersonnelPerformanceTableView

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
router.register(r"feedback-forms", views.FeedbackFormViewSet, basename="feedback-forms")
router.register(
    r"feedback-requests", views.FeedbackRequestViewSet, basename="feedback-requests"
)
router.register(
    r"feedback-entries", views.FeedbackEntryViewSet, basename="feedback-entries"
)

# ─── Profile timeline endpoints ───────────────────────────────────────────────
router.register(r"title-changes", views.TitleChangeViewSet, basename="title-changes")
router.register(r"notices", views.NoticeViewSet, basename="notice")
# Disabled until stock-grant detail endpoint is finalised
# router.register(r"stock-grants", views.StockGrantViewSet, basename="stockgrant")

# ─── URL PATTERNS ────────────────────────────────────────────────────────────────
urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("bepa-callback/", views.BepaCallbackView.as_view(), name="bepa-callback"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("verify-token/", views.VerifyTokenView.as_view(), name="verify-token"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/current-ladder/", views.CurrentLadderView.as_view(), name="current-ladder"),
    path(
        "profile/<uuid:user_uuid>/current-ladder/",
        views.CurrentLadderView.as_view(),
        name="current-ladder-other",
    ),
    path("ladders/", views.LadderListView.as_view(), name="ladders"),
    path("teams/", views.TeamListView.as_view(), name="teams"),
    path("tribes/", views.TribeListView.as_view(), name="tribes"),
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/<uuid:uuid>/", views.UserDetailView.as_view(), name="user-detail"),
    path("templates/", views.TemplatesView.as_view(), name="templates"),
    path("value-tags/", views.ValueTagListView.as_view(), name="value-tags"),
    path("users/<uuid:user_id>/timeline/", UserTimelineView.as_view(), name="user-timeline"),
    path("personnel/performance-table", PersonnelPerformanceTableView.as_view(), name="personnel-performance-table"),
    path("personnel/performance-table/", PersonnelPerformanceTableView.as_view()),
    path("", include(router.urls)),
    path("", include(comments_router.urls)),
    path("", include(summaries_router.urls)),
    path("", include(forms_router.urls)),
    path("", include(team_router.urls)),
]

if settings.SIGNUP_DISABLED != "true":
    urlpatterns.append(path("signup/", views.SignupView.as_view(), name="signup"))
