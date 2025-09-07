from django.urls import path
from .views import (
    RegisterAPIView, VerifyEmailAPIView, ResendVerificationOTPAPIView,
    LoginAPIView, RequestPasswordResetAPIView, ResendPasswordResetOTPAPIView,
    ConfirmPasswordResetAPIView, ChangePasswordAPIView, UserProfileAPIView,
    GetMyProfileView, ProfileView, UpdateMyProfileView, UpdateProfilePhotoView,
    GetAllUsersView, GetUserByIdView, DeleteUserView, SoftDeleteUserView,
    RestoreUserView, MyProfileViewAndUpdate
)

urlpatterns = [
    # ------------------------ Authentication ------------------------ #
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('resend-verification-otp/', ResendVerificationOTPAPIView.as_view(), name='resend-verification-otp'),
    path('login/', LoginAPIView.as_view(), name='login'),

    # ------------------------ Password Management ------------------------ #
    path('request-password-reset/', RequestPasswordResetAPIView.as_view(), name='request-password-reset'),
    path('resend-password-reset-otp/', ResendPasswordResetOTPAPIView.as_view(), name='resend-password-reset-otp'),
    path('confirm-password-reset/', ConfirmPasswordResetAPIView.as_view(), name='confirm-password-reset'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),

    # ------------------------ Profile ------------------------ #
    path('me/', UserProfileAPIView.as_view(), name='user-profile'),
    path('users/me/', GetMyProfileView.as_view(), name='get-my-profile'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/photo/', UpdateProfilePhotoView.as_view(), name='update-profile-photo'),
    path('users/me/update/', UpdateMyProfileView.as_view(), name='update-my-profile'),
    path('users/me/', MyProfileViewAndUpdate.as_view(), name='my-profile'),

    # ------------------------ Admin User Management ------------------------ #
    path('users/', GetAllUsersView.as_view(), name='get-all-users'),  # With filters & search
    path('users/<int:id>/', GetUserByIdView.as_view(), name='get-user-by-id'),
    path('users/<int:id>/delete/', DeleteUserView.as_view(), name='delete-user'),
    path('users/<int:id>/soft-delete/', SoftDeleteUserView.as_view(), name='soft-delete-user'),
    path('users/<int:id>/restore/', RestoreUserView.as_view(), name='restore-user'),
]
