from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from .models import CustomUser, MobileOTP


class JWTAuthenticationTests(APITestCase):
    password = "A-secure-password-872!"
    mobile_number = "+919876543210"

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number=self.mobile_number,
            password=self.password,
            full_name="Test User",
            is_active=True,
            is_mobile_verified=True,
        )

    def login(self, password=None):
        return self.client.post(
            reverse("login"),
            {"mobile_number": self.mobile_number, "password": password or self.password},
            format="json",
        )

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.login()

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["id"], self.user.id)
        self.assertEqual(int(AccessToken(response.data["tokens"]["access"])["user_id"]), self.user.id)

    def test_login_rejects_wrong_password(self):
        response = self.login(password="incorrect-password")

        self.assertEqual(response.status_code, 400)
        self.assertNotIn("tokens", response.data)

    def test_login_rejects_unverified_user(self):
        self.user.is_mobile_verified = False
        self.user.save(update_fields=["is_mobile_verified"])

        response = self.login()

        self.assertEqual(response.status_code, 400)
        self.assertIn("verify", str(response.data).lower())

    def test_access_token_authenticates_current_user(self):
        login_response = self.login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['tokens']['access']}")

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["mobile_number"], self.mobile_number)

    def test_protected_api_allows_valid_access_token(self):
        login_response = self.login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['tokens']['access']}")

        response = self.client.get(reverse("protected-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertIn(self.user.full_name, response.data["message"])

    def test_protected_api_rejects_request_without_access_token(self):
        response = self.client.get(reverse("protected-dashboard"))

        self.assertEqual(response.status_code, 401)

    def test_current_user_rejects_missing_or_invalid_access_token(self):
        self.assertEqual(self.client.get(reverse("current-user")).status_code, 401)

        self.client.credentials(HTTP_AUTHORIZATION="Bearer not-a-jwt")
        self.assertEqual(self.client.get(reverse("current-user")).status_code, 401)

    def test_refresh_endpoint_returns_a_new_access_token(self):
        login_response = self.login()

        response = self.client.post(
            reverse("token_refresh"),
            {"refresh": login_response.data["tokens"]["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_expired_access_token_is_rejected(self):
        token = AccessToken.for_user(self.user)
        token.set_exp(lifetime=timedelta(seconds=-1))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, 401)


class MobileVerificationTests(APITestCase):
    def test_valid_otp_activates_account_and_allows_login(self):
        user = CustomUser.objects.create_user(
            mobile_number="+14155550123",
            password="A-secure-password-872!",
            full_name="Pending User",
            is_active=False,
            is_mobile_verified=False,
        )
        MobileOTP.objects.create(
            user=user,
            otp_hash=make_password("123456"),
            purpose=MobileOTP.OTPPurpose.MOBILE_VERIFICATION,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        response = self.client.post(
            reverse("verify-mobile"),
            {"mobile_number": user.mobile_number, "otp": "123456"},
            format="json",
        )

        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_mobile_verified)
        self.assertTrue(user.otp_records.get().is_used)

        login_response = self.client.post(
            reverse("login"),
            {"mobile_number": user.mobile_number, "password": "A-secure-password-872!"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data["tokens"])

