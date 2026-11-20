
import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomUser


class SignupSerializer(serializers.Serializer):

    full_name = serializers.CharField(
        max_length=150
    )

    mobile_number = serializers.CharField(
        max_length=16
    )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False
    )

    def validate_full_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Full name is required."
            )

        return value

    def validate_mobile_number(self, value):
        value = value.strip()

        # International format, e.g. +919876543210
        if not re.fullmatch(r"\+[1-9]\d{7,14}", value):
            raise serializers.ValidationError(
                "Enter a valid mobile number with country code."
            )

        if CustomUser.objects.filter(
            mobile_number=value
        ).exists():
            raise serializers.ValidationError(
                "This mobile number is already registered."
            )

        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        validate_password(attrs["password"])

        return attrs
