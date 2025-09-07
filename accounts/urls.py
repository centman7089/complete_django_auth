from django.urls import path
from .views import (
    DeleteUserView, GetUserByIdView, LogoutAPIView, MyProfileViewAndUpdate, RegisterAPIView, ResendPasswordResetOTPAPIView, ResendVerificationOTPAPIView, RestoreUserView, SoftDeleteUserView,  UpdateProfilePhotoView, VerifyEmailAPIView, 
    LoginAPIView, RequestPasswordResetAPIView, ConfirmPasswordResetAPIView,
    ChangePasswordAPIView, GetAllUsersView
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('resend-verification-otp/', ResendVerificationOTPAPIView.as_view(), name='resend-verification-otp'),
    path('resend-password-reset-otp/', ResendPasswordResetOTPAPIView.as_view(), name='resend-password-reset-otp'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('request-password-reset/', RequestPasswordResetAPIView.as_view(), name='request-password-reset'),
    path('confirm-password-reset/', ConfirmPasswordResetAPIView.as_view(), name='confirm-password-reset'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    # path('me/', UserProfileAPIView.as_view(), name='user-profile'),
    # path("users/me/", GetMyProfileView.as_view(), name="get-my-profile"),
    # path("profile/", ProfileView.as_view(), name="profile"),
        # profile photo update
    path("profile/photo/", UpdateProfilePhotoView.as_view(), name="update-profile-photo"),

    # user management
    # path("users/", UserListView.as_view(), name="get-all-users"),
     path("users-filter/", GetAllUsersView.as_view(), name="get-all-users-filter"),
    # path("users/<int:id>/", UserDetailView.as_view(), name="get-user-by-id"),
      # Hard delete
    path("users/<int:id>/delete/", DeleteUserView.as_view(), name="delete-user"),

    # Soft delete / restore
    path("users/<int:id>/soft-delete/", SoftDeleteUserView.as_view(), name="soft-delete-user"),
    path("users/<int:id>/restore/", RestoreUserView.as_view(), name="restore-user"),
    path("users/all/<int:id>/", GetUserByIdView.as_view(), name="get-user-by-id"),
    # path("users/me/update/", UpdateMyProfileView.as_view(), name="update-my-profile"),
    path("users/me/", MyProfileViewAndUpdate.as_view(), name="my-profile"),
]
