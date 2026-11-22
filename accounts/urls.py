from django.urls import path

from .views import SignupAPIView, LoginAPIView, VerifyMobileAPIView

urlpatterns = [
    path("signup/",SignupAPIView.as_view(),name="signup"),
    path("login/",LoginAPIView.as_view(),name="login"),
    path("verify-mobile/", VerifyMobileAPIView.as_view(), name="verify-mobile"),

]
