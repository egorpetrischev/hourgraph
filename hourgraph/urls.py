from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import path, include
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, VerifyEmailView, CustomTokenObtainPairView, LogoutView, \
    PasswordResetRequestView, PasswordResetConfirmView, PasswordChangeView, StudentCardViewSet, StudentCardGroupViewSet, \
    LessonTemplateViewSet, WeekViewSet, LessonViewSet
from rest_framework_simplejwt.views import TokenRefreshView


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    return JsonResponse({'is_authenticated': True})

router = DefaultRouter()
router.register(r'studentcards', StudentCardViewSet, basename='studentcards')
router.register(r'studentcardgroups', StudentCardGroupViewSet, basename='studentcardgroups')
router.register(r'lesson-templates', LessonTemplateViewSet, basename='lesson-templates')
router.register(r'lessons', LessonViewSet, basename='lessons')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/<str:key>/', VerifyEmailView.as_view(), name='verify_email'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),
    path('week/', WeekViewSet.as_view(), name='week'),
    path('check-auth/', check_auth, name='check_auth'),
    path('', include(router.urls))
]