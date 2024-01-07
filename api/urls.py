from django.urls import path

from api.views import BepaCallbackView, LoginView, SignupView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("bepa-callback/", BepaCallbackView.as_view(), name="bepa-callback"),
]
