import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 시크릿 키
SECRET_KEY = os.environ.get('SECRET_KEY')

# url
BASE_URL = "cafejari.co.kr"
BASE_IMAGE_URL = "cafejariimage.co.kr"

# 디버그 모드 설정
DEBUG = True

# 로컬환경 / 서버환경 설정
LOCAL = False

# 허용 호스트
ALLOWED_HOSTS = ["*"]

# 사용할 앱
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # rest_framework, jwt
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',

    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.apple',
    'allauth.socialaccount.providers.kakao',

    # dj-rest-auth
    'dj_rest_auth',

    # swagger
    'drf_yasg',

    # s3 연동
    'storages',

    # 카페자리
    'cafe',
    'user',
    'request',
    'leaderboard',
    'shop',
    'notification',
    'cafe_log',
    'data',
    'challenge',

    # crontab
    'django_crontab',
]

# 앱 보안 설정
SEOUL_CITY_DATA_API_KEY = os.environ.get('SEOUL_CITY_DATA_API_KEY')
KAKAO_REST_API_KEY = os.environ.get('KAKAO_REST_API_KEY')
KAKAO_REDIRECT_URL = os.environ.get('KAKAO_REDIRECT_URL')
GIFTISHOW_AUTH_CODE = os.environ.get('GIFTISHOW_AUTH_CODE')
GIFTISHOW_AUTH_TOKEN = os.environ.get('GIFTISHOW_AUTH_TOKEN')
GIFTISHOW_USER_ID = os.environ.get('GIFTISHOW_USER_ID')
NAVER_SERVICE_ID = os.environ.get('NAVER_SERVICE_ID')
NAVER_API_ID = os.environ.get('NAVER_API_ID')
NAVER_API_SECRET = os.environ.get('NAVER_API_SECRET')
NAVER_SMS_CALLING_NUMBER = os.environ.get('NAVER_SMS_CALLING_NUMBER')
ADMIN_PHONE_NUMBER_LIST = [os.environ.get('ADMIN_PHONE_NUMBER_1')]
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_PORT = os.environ.get('DB_PORT')
DB_HOST = 'db' if LOCAL else os.environ.get('DB_HOST')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')

# Sites 앱 설정
SITE_ID = 1

# 미들웨어
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

# Cafejari 앱 설정
RECENT_HOUR = 3  # 몇시간 전 업데이트 로그까지 가져올건지
UPDATE_COOLTIME = 10  # 혼잡도 업데이트 쿨타입(분)
OCCUPANCY_INSUFFICIENT_THRESHOLD = 10  # 혼잡도 데이터 몇개 째부터 포인트 낮출지
OCCUPANCY_ENOUGH_THRESHOLD = 50  # 혼잡도 데이터 몇개 째부터 포인트 더 낮출지
NO_DATA_POINT = 50  # 데이터가 없는카페 포인트
INSUFFICIENT_DATA_POINT = 20  # 데이터가 부족한 카페 포인트
ENOUGH_DATA_POINT = 10  # 데이터가 많은 카페 포인트

# 최초 routing 파일 설정
ROOT_URLCONF = 'cafejari.urls'

# Auth 앱 설정
AUTH_USER_MODEL = 'user.User'
AUTHENTICATION_BACKENDS = [
    'user.backend.UserIdBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Rest-framework 앱 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '8/s',
        'anon': '4/s',
    },
}

# dj-rest-auth 앱 설정
REST_AUTH = {
    'USER_DETAILS_SERIALIZER': 'user.serializers.UserSerializer',
    'SESSION_LOGIN': False,
    'TOKEN_MODEL': 'rest_framework_simplejwt.token_blacklist.models.BlacklistedToken',
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY':False
}

# Simple-jwt 앱 설정
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# All auth 앱 설정
ACCOUNT_EMAIL_VERIFICATION = 'none'
# SOCIALACCOUNT_PROVIDERS = {
    # "apple": {
    #     "APP": {
    #         "client_id": APPLE_CLIENT_ID,
    #         "secret": APPLE_CLIENT_SECRET,
    #         "key": APPLE_PREFIX_KEY,
    #         "certificate_key": "-----BEGIN PRIVATE KEY-----\n"
    #                            f"{APPLE_CERTIFICATE_KEY_LINE_1}\n" +
    #                            f"{APPLE_CERTIFICATE_KEY_LINE_2}\n" +
    #                            f"{APPLE_CERTIFICATE_KEY_LINE_3}\n" +
    #                            f"{APPLE_CERTIFICATE_KEY_LINE_4}\n" +
    #                            "-----END PRIVATE KEY-----"
    #     }
    # }
# }

# cronjab 설정
CRONJOBS = [
    # ('* * * * *', 'cron.congestion.update_congestion_area'),
]

# s3
AWS_S3_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
if not LOCAL:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'cafejari.wsgi.application'

# db설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# 비번 설정
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

# 시간 / 언어
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = False

# static 파일
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# media 파일
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
