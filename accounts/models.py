
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


# =====================================
# CUSTOM USER MANAGER
# =====================================

class CustomUserManager(BaseUserManager):

    def create_user(self, mobile_number, password=None, **extra_fields):

        if not mobile_number:
            raise ValueError("Mobile number is required")

        mobile_number = mobile_number.strip()

        user = self.model(
            mobile_number=mobile_number,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_mobile_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            mobile_number,
            password,
            **extra_fields
        )


# =====================================
# CUSTOM USER MODEL
# =====================================

class CustomUser(AbstractBaseUser, PermissionsMixin):

    mobile_number = models.CharField(
        max_length=16,
        unique=True
    )

    full_name = models.CharField(
        max_length=150
    )

    is_active = models.BooleanField(
        default=False
    )

    is_staff = models.BooleanField(
        default=False
    )

    is_mobile_verified = models.BooleanField(
        default=False
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "mobile_number"

    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.mobile_number


# =====================================
# MOBILE OTP MODEL
# =====================================

class MobileOTP(models.Model):

    class OTPPurpose(models.TextChoices):

        MOBILE_VERIFICATION = (
            "MOBILE_VERIFICATION",
            "Mobile Verification"
        )

        PASSWORD_RESET = (
            "PASSWORD_RESET",
            "Password Reset"
        )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="otp_records"
    )

    otp_hash = models.CharField(
        max_length=128
    )

    purpose = models.CharField(
        max_length=30,
        choices=OTPPurpose.choices
    )

    expires_at = models.DateTimeField()

    attempts = models.PositiveSmallIntegerField(
        default=0
    )

    is_used = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "purpose", "is_used"]
            ),
        ]

    def __str__(self):
        return f"{self.user.mobile_number} - {self.purpose}"
