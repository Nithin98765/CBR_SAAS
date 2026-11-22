
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from .serializers import SignupSerializer,LoginSerializer
from .services import create_pending_user
from .models import CustomUser, MobileOTP
from rest_framework_simplejwt.tokens import RefreshToken



class SignupAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = SignupSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = create_pending_user(
            full_name=serializer.validated_data["full_name"],
            mobile_number=serializer.validated_data["mobile_number"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {
                "success": True,
                "message": "Account created. Please verify your mobile number.",
                "data": {
                    "mobile_number": user.mobile_number,
                    "is_mobile_verified": user.is_mobile_verified,
                },
            },
            status=status.HTTP_201_CREATED,
        )

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data,context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message" : "Login successful.",
                
                "user" : {
                    "id" : user.id,
                    "mobile_number" : user.mobile_number,
                    "full_name" : user.full_name,
                    "is_mobile_verified" : user.is_mobile_verified,
                },
                "tokens" : {
                    "refresh" : str(refresh),
                    "access" : str(refresh.access_token),
                }
            },
            status=status.HTTP_200_OK
        )


class VerifyMobileAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        mobile_number = request.data.get("mobile_number", "").strip()
        otp = request.data.get("otp", "").strip()
        user = CustomUser.objects.filter(mobile_number=mobile_number).first()
        if not user:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        if user.is_mobile_verified:
            return Response({"detail": "Mobile number is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        record = user.otp_records.filter(
            purpose=MobileOTP.OTPPurpose.MOBILE_VERIFICATION,
            is_used=False,
        ).first()
        if not record or record.expires_at <= timezone.now():
            return Response({"detail": "OTP expired. Request a new code."}, status=status.HTTP_400_BAD_REQUEST)
        if record.attempts >= 5:
            return Response({"detail": "Too many attempts. Request a new code."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        if not check_password(otp, record.otp_hash):
            record.attempts += 1
            record.save(update_fields=["attempts"])
            return Response({"detail": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)

        record.is_used = True
        record.save(update_fields=["is_used"])
        user.is_mobile_verified = True
        user.is_active = True
        user.save(update_fields=["is_mobile_verified", "is_active"])
        return Response({"success": True, "message": "Mobile number verified."}, status=status.HTTP_200_OK)
        

