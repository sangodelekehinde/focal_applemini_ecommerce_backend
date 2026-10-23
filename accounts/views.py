# Views for accounts:
#   RegisterView      = creates a new account (your existing view)
#   ResetPasswordView = lets a user set a new password, no email needed

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .serializers import RegisterSerializer

User = get_user_model()


# ---- your existing view (unchanged) ----
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# limits how often one visitor can try the reset
class ResetThrottle(AnonRateThrottle):
    scope = "password_reset"
    rate = "5/hour"  # 5 tries per hour


# ---- NEW: reset the password using username + email ----
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]  # the user is logged out, so no token needed
    authentication_classes = []
    throttle_classes = [ResetThrottle]

    def post(self, request):
        username = request.data.get("username", "").strip()
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        # both boxes must be filled in
        if not username or not email:
            return Response({"detail": "Enter your username and email."}, status=400)

        # 1. the username AND the email must belong to the same account
        user = User.objects.filter(
            username=username, email__iexact=email, is_active=True
        ).first()

        if user is None:
            return Response({"detail": "No account matches that username and email."}, status=400)

        # 2. check the new password is strong enough (Django's built-in rules)
        try:
            validate_password(password, user)
        except ValidationError as error:
            return Response({"detail": " ".join(error.messages)}, status=400)

        # 3. save the new password (it is stored scrambled, never as plain text)
        user.set_password(password)
        user.save()

        return Response({"detail": "Password changed. You can now log in."})