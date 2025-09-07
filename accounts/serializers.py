# # accounts/serializers.py
# from rest_framework import serializers
# from django.contrib.auth import authenticate
# from .models import User
# from .utils import generate_totp, send_otp_email, verify_totp


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)

#     class Meta:
#         model = User
#         fields = ('email', 'first_name', 'last_name', 'password')

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User.objects.create_user(**validated_data)
#         user.set_password(password)
#         user.is_active = True
#         user.is_verified = False
#         user.save()

#         # generate OTP and send email
#         code = generate_totp(user.email)
#         send_otp_email(user.email, code, purpose='email verification')
#         return user


# class VerifyEmailSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     code = serializers.CharField()

#     def validate(self, attrs):
#         email = attrs.get('email')
#         code = attrs.get('code')
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError('No user with this email')

#         if user.is_verified:
#             raise serializers.ValidationError('User already verified')

#         if not verify_totp(email, code):
#             raise serializers.ValidationError('Invalid or expired code')

#         attrs['user'] = user
#         return attrs

#     def save(self, **kwargs):
#         user = self.validated_data['user']
#         user.is_verified = True
#         user.save()
#         return user


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')
#         user = authenticate(username=email, password=password)
#         if not user:
#             raise serializers.ValidationError('Invalid credentials')
#         if not user.is_verified:
#             raise serializers.ValidationError('Email is not verified')
#         attrs['user'] = user
#         return attrs


# class RequestPasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         if not User.objects.filter(email=value).exists():
#             raise serializers.ValidationError('No user with this email')
#         return value

#     def save(self):
#         email = self.validated_data['email']
#         code = generate_totp(email)
#         send_otp_email(email, code, purpose='password reset')
#         return email


# class ConfirmPasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     code = serializers.CharField()
#     new_password = serializers.CharField(min_length=8)

#     def validate(self, attrs):
#         email = attrs.get('email')
#         code = attrs.get('code')
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError('No user with this email')
#         if not verify_totp(email, code):
#             raise serializers.ValidationError('Invalid or expired code')
#         attrs['user'] = user
#         return attrs

#     def save(self):
#         user = self.validated_data['user']
#         user.set_password(self.validated_data['new_password'])
#         user.save()
#         return user


# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField()
#     new_password = serializers.CharField(min_length=8)

#     def validate_old_password(self, value):
#         user = self.context['request'].user
#         if not user.check_password(value):
#             raise serializers.ValidationError('Old password is not correct')
#         return value

#     def save(self, **kwargs):
#         user = self.context['request'].user
#         user.set_password(self.validated_data['new_password'])
#         user.save()
#         return user
    
# class ResendOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     purpose = serializers.ChoiceField(choices=['verification', 'password_reset'])


#     def validate_email(self, value):
#         from .models import User
#         if not User.objects.filter(email=value).exists():
#             raise serializers.ValidationError('No user with this email')
#         return value


#     def save(self):
#         email = self.validated_data['email']
#         purpose = self.validated_data['purpose']
#         code = generate_totp(email)
#         send_otp_email(email, code, purpose=purpose)
#         return email

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
# from .utils import generate_totp, send_otp_email, verify_totp
from rest_framework import serializers
from .models import User, OTP
from .utils import send_otp_email
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from .models import PasswordHistory
from .utils import store_password_history


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)

#     class Meta:
#         model = User
#         fields = (
#             'first_name', 'last_name', 'email', 'password', 'phone',
#             'state', 'city', 'street_address', 'zip_code',
#             'country', 'date_of_birth'
#         )

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User.objects.create_user(**validated_data)
#         user.set_password(password)
#         user.is_active = True
#         user.is_verified = False
#         user.save()

#         # generate OTP and send email
#         code = generate_totp(user.email)
#         send_otp_email(user.email, code, purpose='email verification')
#         return user

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
             'email', 'first_name', 'last_name',
            'password', 'confirm_password',
            'phone', 'state', 'city', 'street_address',
            'zip_code', 'country', 'date_of_birth'
        )
        
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.pop('confirm_password', None)
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.is_verified = False
        user.save()

        # store initial password
        store_password_history(user)

        # Generate OTP in DB
        otp = OTP.create_otp(user, 'verification')
        send_otp_email(user, otp, 'verification')
        return user


# class VerifyEmailSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     code = serializers.CharField()

#     def validate(self, attrs):
#         email = attrs.get('email')
#         code = attrs.get('code')
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError('No user with this email')

#         if user.is_verified:
#             raise serializers.ValidationError('User already verified')

#         if not verify_totp(email, code):
#             raise serializers.ValidationError('Invalid or expired code')

#         attrs['user'] = user
#         return attrs

#     def save(self, **kwargs):
#         user = self.validated_data['user']
#         user.is_verified = True
#         user.save()
#         return user

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user with this email')

        if user.is_verified:
            raise serializers.ValidationError('User already verified')

        try:
            otp = OTP.objects.filter(
                user=user, purpose='verification', is_used=False
            ).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError('No OTP found for this user')

        if otp.is_expired():
            raise serializers.ValidationError('OTP expired')

        if otp.code != code:
            raise serializers.ValidationError('Invalid OTP')

        attrs['user'] = user
        attrs['otp'] = otp
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        otp = self.validated_data['otp']

        user.is_verified = True
        user.save()

        otp.mark_used()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        if not user.is_verified:
            raise serializers.ValidationError('Email is not verified')
        attrs['user'] = user
        return attrs


# class RequestPasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         if not User.objects.filter(email=value).exists():
#             raise serializers.ValidationError('No user with this email')
#         return value

#     def save(self):
#         email = self.validated_data['email']
#         code = generate_totp(email)
#         send_otp_email(email, code, purpose='password reset')
#         return email

class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user with this email')
        return value

    def save(self):
        otp = OTP.create_otp(self.user, 'password_reset')
        send_otp_email(self.user, otp, 'password_reset')
        return self.user.email


# class ConfirmPasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     code = serializers.CharField()
#     new_password = serializers.CharField(min_length=8)

#     def validate(self, attrs):
#         email = attrs.get('email')
#         code = attrs.get('code')

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError('No user with this email')

#         try:
#             otp = OTP.objects.filter(
#                 user=user, purpose='password_reset', is_used=False
#             ).latest('created_at')
#         except OTP.DoesNotExist:
#             raise serializers.ValidationError('No OTP found')

#         if otp.is_expired():
#             raise serializers.ValidationError('OTP expired')

#         if otp.code != code:
#             raise serializers.ValidationError('Invalid OTP')

#         attrs['user'] = user
#         attrs['otp'] = otp
#         return attrs

#     def save(self):
#         user = self.validated_data['user']
#         otp = self.validated_data['otp']

#         user.set_password(self.validated_data['new_password'])
#         user.save()

#         otp.mark_used()
#         return user
# class ConfirmPasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     code = serializers.CharField()
#     new_password = serializers.CharField(min_length=8, write_only=True)
#     confirm_password = serializers.CharField(min_length=8, write_only=True)

#     def validate(self, attrs):
#         email = attrs.get('email')
#         code = attrs.get('code')
#         new_password = attrs.get('new_password')
#         confirm_password = attrs.pop('confirm_password', None)

#         if new_password != confirm_password:
#             raise serializers.ValidationError("Passwords do not match")

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError('No user with this email')

#         try:
#             otp = OTP.objects.filter(
#                 user=user, purpose='password_reset', is_used=False
#             ).latest('created_at')
#         except OTP.DoesNotExist:
#             raise serializers.ValidationError('No OTP found')

#         if otp.is_expired():
#             raise serializers.ValidationError('OTP expired')

#         if otp.code != code:
#             raise serializers.ValidationError('Invalid OTP')

#         attrs['user'] = user
#         attrs['otp'] = otp
#         return attrs

#     def save(self):
#         user = self.validated_data['user']
#         otp = self.validated_data['otp']

#         user.set_password(self.validated_data['new_password'])
#         user.save()

#         otp.mark_used()
#         return user
#updated with passwordHistory

class ConfirmPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        new_password = attrs.get('new_password')
        confirm_password = attrs.pop('confirm_password', None)

        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user with this email')

        # OTP validation logic here (already implemented before)...

        # 🔒 Check against last 5 passwords
        recent_passwords = PasswordHistory.objects.filter(user=user)[:5]
        for entry in recent_passwords:
            if check_password(new_password, entry.password):
                raise serializers.ValidationError("You cannot reuse your last 5 passwords.")

        attrs['user'] = user
        attrs['otp'] = otp
        return attrs

    def save(self):
        user = self.validated_data['user']
        otp = self.validated_data['otp']

        user.set_password(self.validated_data['new_password'])
        user.save()

        # store new password in history
        store_password_history(user)

        otp.mark_used()
        return user



class ConfirmPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user with this email')
        if not verify_totp(email, code):
            raise serializers.ValidationError('Invalid or expired code')
        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


# class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is not correct')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

# class ChangePasswordSerializer(serializers.Serializer):
    # added confirm_password function
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.pop('confirm_password', None)

        if not user.check_password(old_password):
            raise serializers.ValidationError({'old_password': 'Old password is not correct'})

        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])  # 🔒 hashed automatically
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.pop('confirm_password', None)

        if not user.check_password(old_password):
            raise serializers.ValidationError({'old_password': 'Old password is not correct'})

        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})

        # 🔒 Check against last 5 password hashes
        recent_passwords = PasswordHistory.objects.filter(user=user)[:5]
        for entry in recent_passwords:
            if check_password(new_password, entry.password):
                raise serializers.ValidationError("You cannot reuse your last 5 passwords.")

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()

        # store new password in history
        store_password_history(user)

        return user


# class ResendOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     purpose = serializers.ChoiceField(choices=['verification', 'password_reset'])

#     def validate_email(self, value):
#         if not User.objects.filter(email=value).exists():
#             raise serializers.ValidationError('No user with this email')
#         return value

#     def save(self):
#         email = self.validated_data['email']
#         purpose = self.validated_data['purpose']
#         code = generate_totp(email)
#         send_otp_email(email, code, purpose=purpose)
#         return email




class ResendVerificationOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user with this email")
        if self.user.is_verified:
            raise serializers.ValidationError("User is already verified")

        # rate limit: max 3 OTPs in 10 minutes
        recent_otps = OTP.objects.filter(
            user=self.user, purpose='verification',
            created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
        )
        if recent_otps.count() >= 3:
            raise serializers.ValidationError("Too many OTP requests. Try again later.")
        return value

    def save(self):
        otp = OTP.create_otp(self.user, 'verification')
        send_otp_email(self.user, otp, 'verification')
        return otp


class ResendPasswordResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user with this email")

        # rate limit
        recent_otps = OTP.objects.filter(
            user=self.user, purpose='password_reset',
            created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
        )
        if recent_otps.count() >= 3:
            raise serializers.ValidationError("Too many OTP requests. Try again later.")
        return value

    def save(self):
        otp = OTP.create_otp(self.user, 'password_reset')
        send_otp_email(self.user, otp, 'password_reset')
        return otp


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone',
            'state', 'city', 'street_address', 'zip_code',
            'country', 'date_of_birth', 'is_verified', 'date_joined'
        )
        read_only_fields = ('id', 'is_verified', 'date_joined')
        
class ProfileSerializer(serializers.ModelSerializer):
    avatar_initials = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "phone", "state", "city",
            "street_address", "zip_code", "country", "date_of_birth",
            "profile_photo", "avatar_initials"
        ]
        read_only_fields = ["email", "avatar_initials"]

    def update(self, instance, validated_data):
        new_photo = validated_data.pop("profile_photo", None)

        # Handle photo replacement
        if new_photo:
            instance.set_profile_photo(new_photo)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_avatar_initials(self, obj):
        return obj.avatar_initials


class UpdateProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_photo"]

    def update(self, instance, validated_data):
        new_photo = validated_data.get("profile_photo")
        if new_photo:
            instance.set_profile_photo(new_photo)  # deletes old photo + saves new
        return instance


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ["id", "purpose", "code", "created_at", "is_used"]


class PasswordHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordHistory
        fields = ["id", "password", "created_at"]


class UserDetailSerializerWithDetails(serializers.ModelSerializer):
    otps = OTPSerializer(many=True, read_only=True, source="otp_set")
    password_history = PasswordHistorySerializer(many=True, read_only=True, source="passwordhistory_set")

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone",
            "state", "city", "street_address", "zip_code",
            "country", "date_of_birth", "profile_photo",
            "is_active", "is_verified", "is_staff", "date_joined",
            "otps", "password_history"
        ]

class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone",
            "state", "city", "street_address", "zip_code",
            "country", "date_of_birth", "profile_photo",
            "is_active", "is_verified", "date_joined"
        ]

class UpdateMyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "phone", "state", "city",
            "street_address", "zip_code", "country", "date_of_birth"
        ]

    def to_representation(self, instance):
        """Ensure null fields return as empty string instead of None."""
        data = super().to_representation(instance)
        for field, value in data.items():
            data[field] = value if value is not None else ""
        return data

class GetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone",
            "state", "city", "street_address", "zip_code",
            "country", "date_of_birth", "profile_photo",
            "is_active", "is_verified", "date_joined"
        ]
        read_only_fields = ["id", "email", "is_active", "is_verified", "date_joined", "profile_photo"]

    def to_representation(self, instance):
        """Ensure null fields return as empty string instead of None."""
        data = super().to_representation(instance)
        for field, value in data.items():
            data[field] = value if value is not None else ""
        return data
