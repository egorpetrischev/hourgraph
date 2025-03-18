from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.urls import reverse
from allauth.account.models import EmailAddress, EmailConfirmation
from hourgraph.models import Users, StudentCard, StudentCardGroup


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ('email', 'password', 'name')

    @staticmethod
    def send_confirmation_email(request, user):
        email_address = user.emailaddress_set.get(email=user.email)
        confirmation = EmailConfirmation.create(email_address)
        key = confirmation.key

        confirm_url = request.build_absolute_uri(
            reverse('verify_email', args=[key])
        )

        subject = 'Подтвердите ваш email'
        message = f'Для подтверждения email перейдите по ссылке: {confirm_url}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

    def create(self, validated_data):
        user = Users.objects.create(
            email=validated_data['email'],
            name=validated_data['name'],
            password=make_password(validated_data['password']),
        )
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
        self.send_confirmation_email(self.context['request'], user)  # Отправка письма
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Вызов стандартной логики валидации
        data = super().validate(attrs)

        # Получаем пользователя
        user = self.user

        # Проверяем, подтвержден ли email
        email_address = EmailAddress.objects.filter(user=user, email=user.email).first()
        if not email_address or not email_address.verified:
            raise serializers.ValidationError("Email не подтвержден. Пожалуйста, подтвердите ваш email.")

        # Добавляем дополнительные данные в ответ (опционально)
        data['name'] = user.name
        data['email'] = user.email

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Старый пароль неверный.')
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Пароль должен содержать минимум 8 символов.')
        return value


class StudentCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCard
        fields = ['id', 'name', 'surname', 'contacts', 'comment', 'address']


class StudentCardGroupSerializer(serializers.ModelSerializer):
    students = StudentCardSerializer(many=True, read_only=True)
    class Meta:
        model = StudentCardGroup
        fields = ['id', 'students', 'name', 'comment']

