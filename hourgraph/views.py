from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from allauth.account.models import EmailConfirmation
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str

from .models import Users
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer, PasswordResetRequestSerializer, \
    PasswordResetConfirmSerializer, PasswordChangeSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = []


class VerifyEmailView(APIView):
    permission_classes = []
    def post(self, request, key):
        email_address = get_object_or_404(EmailConfirmation, key=key)

        # Убедимся, что поле `sent` установлено
        if email_address.sent is None:
            email_address.sent = timezone.now()
            email_address.save()

        email_address.confirm(request)

        email_address.confirm(request)
        return Response({'status': 'email verified'})


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()  # Добавляем refresh-токен в черный список
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = Users.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = f"127.0.0.1/8080/{reset_url}"  # Укажите URL вашего фронтенда settings.FRONTEND_URL
            send_mail(
                'Сброс пароля',
                f'Перейдите по ссылке для сброса пароля: {reset_url}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({"message": "Ссылка для сброса пароля отправлена на ваш email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = []
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uidb64']))
                user = Users.objects.get(pk=uid)
                token = serializer.validated_data['token']
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({"message": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Неверный токен."}, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
                return Response({"error": "Неверный UID."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = make_password(serializer.validated_data['new_password'])
            user.password = new_password
            user.save()
            return Response({'message': 'Пароль успешно изменен.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
