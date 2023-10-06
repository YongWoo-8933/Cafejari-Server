import os
import environ
from datetime import timedelta
from pathlib import Path

# 환경설정
env = environ.Env(
    DEBUG=(bool, True)
)

# 루트 폴더
BASE_DIR = Path(__file__).resolve().parent.parent

# .env에서 파일 읽기
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 디버그 모드
DEBUG = env('DEBUG')

# 시크릿 키
SECRET_KEY = env('SECRET_KEY')

# 도메인
BASE_DOMAIN = "cafejari.co.kr"
BASE_IMAGE_DOMAIN = "cafejariimage.co.kr"

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
    'django.contrib.gis',

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
    'app_config',
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
SEOUL_CITY_DATA_API_KEY = env('SEOUL_CITY_DATA_API_KEY')
KAKAO_REST_API_KEY = env('KAKAO_REST_API_KEY')
KAKAO_REDIRECT_URL = env('KAKAO_REDIRECT_URL')
APPLE_REDIRECT_URL = env('APPLE_REDIRECT_URL')
APPLE_CLIENT_ID = env('APPLE_CLIENT_ID')
APPLE_KEY_ID = env('APPLE_KEY_ID')
APPLE_APP_ID_PREFIX = env('APPLE_APP_ID_PREFIX')
APPLE_CERTIFICATE_KEY = f"""-----BEGIN PRIVATE KEY-----
{env('APPLE_CERTIFICATE_KEY_1st_line')}
{env('APPLE_CERTIFICATE_KEY_2nd_line')}
{env('APPLE_CERTIFICATE_KEY_3rd_line')}
{env('APPLE_CERTIFICATE_KEY_4th_line')}
-----END PRIVATE KEY-----"""
GIFTISHOW_AUTH_CODE = env('GIFTISHOW_AUTH_CODE')
GIFTISHOW_AUTH_TOKEN = env('GIFTISHOW_AUTH_TOKEN')
GIFTISHOW_USER_ID = env('GIFTISHOW_USER_ID')
NAVER_SERVICE_ID = env('NAVER_SERVICE_ID')
NAVER_API_ID = env('NAVER_API_ID')
NAVER_API_SECRET = env('NAVER_API_SECRET')
NAVER_GEO_KEY_ID = env('NAVER_GEO_KEY_ID')
NAVER_GEO_KEY = env('NAVER_GEO_KEY')
NAVER_SMS_CALLING_NUMBER = env('NAVER_SMS_CALLING_NUMBER')
ADMIN_PHONE_NUMBER_LIST = [env('ADMIN_PHONE_NUMBER_1')]
DB_NAME = env('DB_NAME')
DB_USER = env('DB_USER')
DB_PASSWORD = env('DB_PASSWORD')
DB_PORT = env('DB_PORT')
DB_HOST = 'db' if LOCAL else env('DB_HOST')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
GOOGLE_PLACE_API_KEY = env('GOOGLE_PLACE_API_KEY')

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
RECENT_HOUR = 2  # 몇시간 전 업데이트 로그까지 가져올건지
UPDATE_COOLTIME = 10  # 혼잡도 업데이트 쿨타입(분)
OCCUPANCY_INSUFFICIENT_THRESHOLD = 6  # 혼잡도 데이터 몇개 째부터 포인트 낮출지
OCCUPANCY_ENOUGH_THRESHOLD = 16  # 혼잡도 데이터 몇개 째부터 포인트 더 낮출지
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
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=180),
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# All auth 앱 설정
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_PROVIDERS = {
    "apple": {
        "APP": {
            "client_id": APPLE_CLIENT_ID,
            "secret": APPLE_KEY_ID,
            "key": APPLE_APP_ID_PREFIX,
            "certificate_key": APPLE_CERTIFICATE_KEY
        }
    }
}

# cronjab 설정
CRONJOBS = [
    ('25 7 * * *', 'cron.congestion.update_congestion_area_cron'),
    ('30 7 * * *', 'cron.item.update_item_list_cron'),
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
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
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

# log 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'INFO',
            'encoding': 'utf-8',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'log/test.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'my': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    }
}

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
