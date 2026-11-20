
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, MobileOTP


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    ordering = ["mobile_number"]

    list_display = [
        "mobile_number",
        "full_name",
        "is_active",
        "is_mobile_verified",
        "is_staff",
    ]

    search_fields = [
        "mobile_number",
        "full_name",
    ]

    fieldsets = (
        (None, {
            "fields": ("mobile_number", "password")
        }),

        ("Personal Information", {
            "fields": ("full_name",)
        }),

        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "is_mobile_verified",
                "groups",
                "user_permissions",
            )
        }),

        ("Important Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "mobile_number",
                "full_name",
                "password",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    filter_horizontal = [
        "groups",
        "user_permissions",
    ]

    readonly_fields = [
        "date_joined",
        "last_login",
    ]


@admin.register(MobileOTP)
class MobileOTPAdmin(admin.ModelAdmin):

    list_display = [
        "user",
        "purpose",
        "expires_at",
        "attempts",
        "is_used",
    ]

    list_filter = [
        "purpose",
        "is_used",
    ]

    search_fields = [
        "user__mobile_number",
    ]

    readonly_fields = [
        "otp_hash",
    ]
