from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse
from cloudinary.uploader import destroy
from rest_framework.parsers import MultiPartParser, FormParser


from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


from .models import User
from .serializers import (
    GetProfileSerializer, LogoutSerializer,  RegisterSerializer,
    ResendPasswordResetOTPSerializer, ResendVerificationOTPSerializer,
     UpdateProfilePhotoSerializer,
    UserDetailSerializerWithDetails, UserSerializer, VerifyEmailSerializer,
    LoginSerializer, RequestPasswordResetSerializer, ConfirmPasswordResetSerializer,
    ChangePasswordSerializer
)

# ------------------------ Auth Endpoints ------------------------ #

@extend_schema(
    summary="Register a new user",
    request=RegisterSerializer,
    responses={201: UserSerializer}
)
class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT token
        refresh = TokenObtainPairSerializer.get_token(user)
        tokens = {'refresh': str(refresh), 'access': str(refresh.access_token)}

        return Response({
            'detail': 'User created. OTP sent to email.',
            'tokens': tokens,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Login user and return JWT tokens",
    request=LoginSerializer,
    responses={200: UserSerializer}
)
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = TokenObtainPairSerializer.get_token(user)
        tokens = {'refresh': str(refresh), 'access': str(refresh.access_token)}

        return Response({
            'tokens': tokens,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        


@extend_schema(
    summary="Logiout User and destroy jwt",
    request=LoginSerializer,
    responses={200: UserSerializer}
)
class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# ------------------------ OTP Endpoints ------------------------ #

@extend_schema(
    summary="Verify email using OTP",
    description="Verify a user's email by submitting the OTP code sent to their email.",
    request=VerifyEmailSerializer,
    responses={200: OpenApiResponse(description="Email verified successfully")},
)
class VerifyEmailAPIView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Email verified successfully'}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Resend verification OTP",
    description="Resend a One-Time Password (OTP) for email verification purposes.",
    request=ResendVerificationOTPSerializer,
    responses={200: OpenApiResponse(description="Verification OTP sent successfully")},
)
class ResendVerificationOTPAPIView(generics.GenericAPIView):
    serializer_class = ResendVerificationOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Verification OTP sent.'}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Request password reset OTP",
    description="Request a One-Time Password (OTP) to reset your password.",
    request=RequestPasswordResetSerializer,
    responses={200: OpenApiResponse(description="Password reset OTP sent successfully")},
)
class RequestPasswordResetAPIView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset OTP sent to email.'}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Resend password reset OTP",
    description="Resend a One-Time Password (OTP) for password reset purposes.",
    request=ResendPasswordResetOTPSerializer,
    responses={200: OpenApiResponse(description="Password reset OTP sent successfully")},
)
class ResendPasswordResetOTPAPIView(generics.GenericAPIView):
    serializer_class = ResendPasswordResetOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset OTP sent.'}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Confirm password reset using OTP",
    request=ConfirmPasswordResetSerializer,
    responses={200: OpenApiResponse(description="Password reset successfully")}
)
class ConfirmPasswordResetAPIView(generics.GenericAPIView):
    serializer_class = ConfirmPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset successfully'}, status=status.HTTP_200_OK)


# ------------------------ Password Change ------------------------ #

@extend_schema(
    summary="Change logged-in user's password",
    request=ChangePasswordSerializer,
    responses={200: OpenApiResponse(description="Password changed successfully")}
)
class ChangePasswordAPIView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)


# ------------------------ Profile Endpoints ------------------------ #

@extend_schema(
    summary="Retrieve and update logged-in user's profile",
    request=GetProfileSerializer,
    responses={200: GetProfileSerializer}
)
class MyProfileViewAndUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = GetProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(
    summary="Update only profile photo",
    request=UpdateProfilePhotoSerializer,
    responses={200: UpdateProfilePhotoSerializer}
)
class UpdateProfilePhotoView(generics.UpdateAPIView):
    serializer_class = UpdateProfilePhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # <-- Enable multipart

    def get_object(self):
        return self.request.user


# ------------------------ Admin User Management ------------------------ #

@extend_schema(
    summary="Get all users (Admin only)",
    responses={200: UserSerializer(many=True)}
)
class GetAllUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = User.objects.all()
        status_param = self.request.query_params.get("status")
        search_param = self.request.query_params.get("search")

        if status_param == "active":
            queryset = queryset.filter(is_active=True)
        elif status_param == "inactive":
            queryset = queryset.filter(is_active=False)

        if search_param:
            queryset = queryset.filter(
                Q(email__icontains=search_param) |
                Q(first_name__icontains=search_param) |
                Q(last_name__icontains=search_param) |
                Q(phone__icontains=search_param)
            )

        return queryset.order_by("-date_joined")


@extend_schema(
    summary="Get user by ID (Admin only)",
    responses={200: UserDetailSerializerWithDetails}
)
class GetUserByIdView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializerWithDetails
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"


@extend_schema(
    summary="Delete user by ID (Admin only)",
    responses={200: OpenApiResponse(description="User permanently deleted")}
)
class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def perform_destroy(self, instance):
        if instance.profile_photo and hasattr(instance.profile_photo, "public_id"):
            try:
                destroy(instance.profile_photo.public_id)
            except Exception as e:
                print(f"⚠️ Failed to delete Cloudinary image: {e}")
        instance.delete()

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        self.perform_destroy(user)
        return Response({"detail": "User permanently deleted."}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Soft delete (deactivate) user by ID (Admin only)",
    responses={200: OpenApiResponse(description="User soft deleted")}
)
class SoftDeleteUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"detail": "User soft deleted (deactivated)."}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Restore deactivated user by ID (Admin only)",
    responses={200: OpenApiResponse(description="User restored")}
)
class RestoreUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"detail": "User restored successfully."}, status=status.HTTP_200_OK)
