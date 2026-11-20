
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import SignupSerializer
from .services import create_pending_user


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
