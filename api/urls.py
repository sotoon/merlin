from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import BepaCallbackView, LoginView, SignupView, VerifyTokenView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("bepa-callback/", BepaCallbackView.as_view(), name="bepa-callback"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("verify-token/", VerifyTokenView.as_view(), name="verify-token"),
]
