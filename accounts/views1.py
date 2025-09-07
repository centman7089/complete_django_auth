# from rest_framework import generics, status, permissions
# from rest_framework.response import Response
# from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from .serializers import (
#     RegisterSerializer, VerifyEmailSerializer, LoginSerializer,
#     RequestPasswordResetSerializer, ConfirmPasswordResetSerializer,
#     ChangePasswordSerializer, ResendOTPSerializer
# )
# from .models import User


# class RegisterAPIView(generics.CreateAPIView):
#     serializer_class = RegisterSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'detail': 'User created. OTP sent to email.'}, status=status.HTTP_201_CREATED)


# class VerifyEmailAPIView(generics.GenericAPIView):
#     serializer_class = VerifyEmailSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'detail': 'Email verified successfully'}, status=status.HTTP_200_OK)


# class ResendOTPAPIView(generics.GenericAPIView):
#     serializer_class = ResendOTPSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'detail': 'New OTP sent to email.'}, status=status.HTTP_200_OK)


# class LoginAPIView(generics.GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']

#         # Generate JWT token
#         refresh = TokenObtainPairSerializer.get_token(user)
#         data = {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }
#         return Response(data, status=status.HTTP_200_OK)


# class RequestPasswordResetAPIView(generics.GenericAPIView):
#     serializer_class = RequestPasswordResetSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'detail': 'Password reset OTP sent to email.'}, status=status.HTTP_200_OK)


# class ConfirmPasswordResetAPIView(generics.GenericAPIView):
#     serializer_class = ConfirmPasswordResetSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'detail': 'Password reset successfully'}, status=status.HTTP_200_OK)


# class ChangePasswordAPIView(generics.GenericAPIView):
#     serializer_class = ChangePasswordSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)

from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from .models import User
from .serializers import (
    GetProfileSerializer, MyProfileSerializer, RegisterSerializer, ResendPasswordResetOTPSerializer, ResendVerificationOTPSerializer, UpdateMyProfileSerializer, UpdateProfilePhotoSerializer, UserDetailSerializerWithDetails, UserSerializer, VerifyEmailSerializer, LoginSerializer,
    RequestPasswordResetSerializer, ConfirmPasswordResetSerializer,
    ChangePasswordSerializer, ProfileSerializer
)
from cloudinary.uploader import destroy
from rest_framework.permissions import IsAuthenticated


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # generate JWT token for new user
        refresh = TokenObtainPairSerializer.get_token(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response({
            'detail': 'User created. OTP sent to email.',
            'tokens': tokens,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT token
        refresh = TokenObtainPairSerializer.get_token(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response({
            'tokens': tokens,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class VerifyEmailAPIView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Email verified successfully'}, status=status.HTTP_200_OK)


# class ResendOTPAPIView(generics.GenericAPIView):
#     serializer_class = ResendOTPSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'detail': 'New OTP sent to email.'}, status=status.HTTP_200_OK)


# class LoginAPIView(generics.GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']

#         # Generate JWT token
#         refresh = TokenObtainPairSerializer.get_token(user)
#         data = {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }
#         return Response(data, status=status.HTTP_200_OK)


class RequestPasswordResetAPIView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset OTP sent to email.'}, status=status.HTTP_200_OK)


class ConfirmPasswordResetAPIView(generics.GenericAPIView):
    serializer_class = ConfirmPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset successfully'}, status=status.HTTP_200_OK)


class ChangePasswordAPIView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class ResendVerificationOTPAPIView(generics.GenericAPIView):
    serializer_class = ResendVerificationOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Verification OTP sent.'}, status=status.HTTP_200_OK)


class ResendPasswordResetOTPAPIView(generics.GenericAPIView):
    serializer_class = ResendPasswordResetOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset OTP sent.'}, status=status.HTTP_200_OK)

# get my profile retrieves update   
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
# ✅ Update profile photo only
class UpdateProfilePhotoView(generics.UpdateAPIView):
    serializer_class = UpdateProfilePhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ✅ Get all users (Admin-only, for example)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class GetAllUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = User.objects.all()
        status_param = self.request.query_params.get("status")
        search_param = self.request.query_params.get("search")

        # Status filter
        if status_param == "active":
            queryset = queryset.filter(is_active=True)
        elif status_param == "inactive":
            queryset = queryset.filter(is_active=False)

        # Search filter
        if search_param:
            queryset = queryset.filter(
                Q(email__icontains=search_param) |
                Q(first_name__icontains=search_param) |
                Q(last_name__icontains=search_param) |
                Q(phone__icontains=search_param)
            )

        return queryset.order_by("-date_joined")

# ✅ Get user by ID (Admin-only, for example)
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"
    
class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def perform_destroy(self, instance):
        # Cloudinary cleanup
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


class SoftDeleteUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"detail": "User soft deleted (deactivated)."}, status=status.HTTP_200_OK)


class RestoreUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"detail": "User restored successfully."}, status=status.HTTP_200_OK)
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def perform_destroy(self, instance):
        # Delete profile photo from Cloudinary if exists
        if instance.profile_photo and instance.profile_photo.public_id:
            try:
                destroy(instance.profile_photo.public_id)
            except Exception as e:
                print(f"⚠️ Failed to delete Cloudinary image: {e}")

        instance.delete()

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        self.perform_destroy(user)
        return Response({"detail": "User deleted successfully."}, status=status.HTTP_200_OK)
    
class GetUserByIdView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializerWithDetails
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"
    
class GetMyProfileView(generics.RetrieveAPIView):
    serializer_class = MyProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Instead of looking up by pk, just return the authenticated user
        return self.request.user
    
class UpdateMyProfileView(generics.UpdateAPIView):
    serializer_class = UpdateMyProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# it retrieves and update
class MyProfileViewAndUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = GetProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user