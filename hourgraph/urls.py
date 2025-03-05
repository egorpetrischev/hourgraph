from django.urls import path
from .views import UserRegistrationView, VerifyEmailView, CustomTokenObtainPairView, LogoutView, \
    PasswordResetRequestView, PasswordResetConfirmView, PasswordChangeView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/<str:key>/', VerifyEmailView.as_view(), name='verify_email'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('change-password/', PasswordChangeView.as_view(), name='change_password')
]