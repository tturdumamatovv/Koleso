from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.contrib.auth import authenticate

from apps.authentication.models import (
    User,
    UserAddress,
    WorkShift
)
from config import settings


class UserBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['bonus']


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'full_name', 'date_of_birth', 'email')
        read_only_fields = ('full_name', 'date_of_birth', 'email')


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4)
    fcm_token = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    receive_notifications = serializers.BooleanField(required=False, allow_null=True)


class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    has_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'profile_picture', 'full_name', 'date_of_birth',
                  'email', 'first_visit', 'has_profile_picture', 'receive_notifications')
        read_only = ('receive_notifications',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if not ret['profile_picture']:
            if request is not None:
                ret['profile_picture'] = request.build_absolute_uri(
                    settings.MEDIA_URL + 'profile_pictures/default-user.jpg')
            else:
                ret['profile_picture'] = settings.MEDIA_URL + 'profile_pictures/default-user.jpg'
        return ret

    def get_has_profile_picture(self, instance):
        return bool(instance.profile_picture)


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'city', 'apartment_number', 'entrance',
                  'floor', 'intercom', 'created_at', 'is_primary', 'longitude', 'latitude']  # Include 'is_primary'
        read_only_fields = ['user', 'created_at']


class UserAddressDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [field.name for field in UserAddress._meta.fields if field.name not in ('id', 'user')]


class UserAddressUpdateSerializer(serializers.ModelSerializer):
    city = serializers.CharField(required=False)
    is_primary = serializers.BooleanField(required=False)  # Include 'is_primary' as an optional field

    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'city', 'apartment_number', 'entrance',
                  'floor', 'intercom', 'created_at', 'is_primary', 'longitude', 'latitude']  # Include 'is_primary'
        read_only_fields = ['user', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    fcm_token = serializers.CharField(max_length=255, required=False)
    receive_notifications = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = User
        fields = ('fcm_token', 'receive_notifications')


class CourierCollectorLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13)
    password = serializers.CharField(write_only=True, max_length=128)
    fcm_token = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    receive_notifications = serializers.BooleanField(required=False, allow_null=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')
        fcm_token = data.get('fcm_token')
        receive_notifications = data.get('receive_notifications')

        if phone_number and password:
            # Проверка на наличие пользователя с указанным номером телефона
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                raise ValidationError({"error_phone": "Неверный номер телефона."})

            # Проверка на правильность пароля
            if not user.check_password(password):
                raise ValidationError({"error_password": "Неверный пароль."})

            # Проверка на роль пользователя
            if user.role not in ['delivery', 'collector']:
                raise ValidationError({
                    "error_role": "У пользователя нет прав для доступа в систему как курьер или сборщик."
                })

            # Сохраняем fcm_token и receive_notifications, если они переданы
            if fcm_token:
                user.fcm_token = fcm_token
            if receive_notifications is not None:
                user.receive_notifications = receive_notifications
            user.save()

            data['user'] = user
        else:
            raise ValidationError({"error_phone": "Необходимо указать номер телефона и пароль."})

        return data


class WorkShiftSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)
    end_time = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)
    class Meta:
        model = WorkShift
        fields = ['user', 'start_time', 'end_time', 'duration', 'is_open']  # Добавляем поле is_open
        read_only_fields = ['user', 'start_time', 'end_time', 'duration', 'is_open']

