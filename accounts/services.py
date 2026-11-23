
import secrets

from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone

from .models import CustomUser, MobileOTP


@transaction.atomic
def create_pending_user(*, full_name, email, mobile_number, password):

    # Create an inactive user account
    user = CustomUser.objects.create_user(
        mobile_number=mobile_number,
        password=password,
        full_name=full_name,
        email=email,
        is_active=False,
        is_mobile_verified=False,
    )

    # Generate a six-digit OTP
    otp = f"{secrets.randbelow(1000000):06d}"

    # Hash OTP before saving
    otp_hash = make_password(otp)

    # Save OTP with five-minute expiry
    MobileOTP.objects.create(
        user=user,
        otp_hash=otp_hash,
        purpose=MobileOTP.OTPPurpose.MOBILE_VERIFICATION,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    # Development only: display OTP in terminal
    print(
        f"[DEV OTP] Mobile: {mobile_number} | OTP: {otp}"
    )

    return user
