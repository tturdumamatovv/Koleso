from django.urls import path

from apps.authentication.api.views import (
    UserLoginView,
    VerifyCodeView,
    UserProfileUpdateView,
    UserAddressCreateAPIView,
    UserAddressUpdateAPIView,
    UserAddressDeleteAPIView,
    UserDeleteAPIView,
    NotificationSettingsAPIView,
    UserBonusView,
    CourierCollectorLoginView,
    ToggleShiftView
    )

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user_registration'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile'),
    path('addresses/', UserAddressCreateAPIView.as_view(), name='create_address'),
    path('addresses/<int:pk>/update/', UserAddressUpdateAPIView.as_view(), name='update_address'),
    path('addresses/<int:pk>/delete/', UserAddressDeleteAPIView.as_view(), name='delete_address'),
    path('user-delete/', UserDeleteAPIView.as_view(), name='user-delete'),
    path('notification-settings/', NotificationSettingsAPIView.as_view(), name='notification-settings'),
    path('bonus/', UserBonusView.as_view(), name='user-bonus'),
    path('login/courier_collector/', CourierCollectorLoginView.as_view(), name='courier-collector-login'),
    path('shift/toggle/', ToggleShiftView.as_view(), name='toggle-shift'),
]
