from django.urls import path

from .views import (
    SignupAPIView,
    LoginAPIView,
    VerifyMobileAPIView,
    CurrentUserAPIView,
    protected_dashboard_api,
)

urlpatterns = [
    path("signup/",SignupAPIView.as_view(),name="signup"),
    path("login/",LoginAPIView.as_view(),name="login"),
    path("verify-mobile/", VerifyMobileAPIView.as_view(), name="verify-mobile"),
    path("me/", CurrentUserAPIView.as_view(), name="current-user"),
    path("protected/", protected_dashboard_api, name="protected-dashboard"),

]
