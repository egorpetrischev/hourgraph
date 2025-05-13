from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', # drf
    # 'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'hourgraph', # app
    'corsheaders', #cors
    'django.contrib.sites', #allauth
    'allauth',
    'allauth.account',
]

AUTH_USER_MODEL = 'hourgraph.Users'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# """ JWT """
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(weeks=100),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
# """"""

AUTHENTICATION_BACKENDS = [
    # Необходимо для входа в систему через username в Django admin
    'django.contrib.auth.backends.ModelBackend',

    # Специальный метод аутентификации allauth, например, через email
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Настройки allauth
ACCOUNT_EMAIL_REQUIRED = True  # Обязательное поле email
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Подтверждение email обязательно
ACCOUNT_UNIQUE_EMAIL = True  # Уникальный email
ACCOUNT_USERNAME_REQUIRED = False  # Не использовать username
ACCOUNT_LOGIN_METHODS = {'email'} # Использовать email для входа

# Настройки для отправки писем (например, через консоль для разработки)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_ID = 1
#_________

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://192.168.1.6:3000",  # Разрешить запросы от Vue.js
    'http://localhost:3000',
    'http://127.0.0.1:3000'
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Используемый движок базы данных
        'NAME': os.getenv('DB_NAME'),                    # Имя базы данных
        'USER': os.getenv('DB_USER'),                    # Имя пользователя базы данных
        'PASSWORD': os.getenv('DB_PASSWORD'),            # Пароль пользователя базы данных
        'HOST': 'localhost',                       # Хост базы данных (обычно 'localhost' или '127.0.0.1')
        'PORT': '5432',                            # Порт базы данных (по умолчанию 5432 для PostgreSQL)
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
