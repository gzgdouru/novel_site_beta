"""
Django settings for novel_site project.

Generated by 'django-admin startproject' using Django 1.11.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os, sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k^g*ftz$%r8)ur5_rmnb-!ry9@vudt1tbndazblsh$3dpxea2b'

if sys.platform[:3] == "win":
    is_beta = True
else:
    is_beta = False

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if is_beta else False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 自定义app
    'novel',
    'authors',
    'users',
    'operation',
    'api',

    # 第三方app
    'xadmin',
    'crispy_forms',
    'social_django',
    'captcha',
    'django_extensions',
    'rest_framework',
    'django_filters',
]

AUTH_USER_MODEL = 'users.UserProfile'

AUTHENTICATION_BACKENDS = [
    'users.views.MyAuthBackend',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.weibo.WeiboOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

if is_beta:
    # 测试环境
    CUSTOM_DNS = "http://127.0.0.1:8000"

    SOCIAL_AUTH_GITHUB_KEY = '13b17047728735cf1a6c'
    SOCIAL_AUTH_GITHUB_SECRET = '63c3cfc90260d747b6625d9eb9881ad115b7a2df'
    SOCIAL_AUTH_WEIBO_KEY = '3374124543'
    SOCIAL_AUTH_WEIBO_SECRET = '0388e0f30e5dcc97295177aa11a727b0'
else:
    # 服务器环境
    CUSTOM_DNS = "http://ljwancaiji.com"

    SOCIAL_AUTH_GITHUB_KEY = '809e80bff80b8f0fe385'
    SOCIAL_AUTH_GITHUB_SECRET = '95d128b7f54e8a1965bc29f986e461d470bd4753'
    SOCIAL_AUTH_WEIBO_KEY = '4069391206'
    SOCIAL_AUTH_WEIBO_SECRET = 'fd3576c9955f04145ae3c3dbe9550e4f'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',    # 缓存, 必须在最前面
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware', # 缓存, 必须在最后面
]

ROOT_URLCONF = 'novel_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'novel_site.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'novel_site_beta',
        'USER': 'ouru',
        'PASSWORD': '5201314Ouru...',
        'HOST': '193.112.150.18',
        'PORT': '3306',
        'OPTIONS': {'init_command': 'SET default_storage_engine=INNODB;'},
    }
}

# #缓存
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "PASSWORD": "123456",
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 上传文件保存路径
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

from django.contrib import messages

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

# 邮件设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = False  # 是否使用TLS安全传输协议(用于在两个通信应用程序之间提供保密性和数据完整性。)
EMAIL_USE_SSL = True  # 是否使用SSL加密，qq企业邮箱要求使用
EMAIL_HOST = 'smtp.163.com'  # 发送邮件的邮箱 的 SMTP服务器，这里用了163邮箱
EMAIL_PORT = 465
EMAIL_HOST_USER = "anjubaoouru@163.com"
EMAIL_HOST_PASSWORD = "qq5201314ouru"

# 线上邮件设置
ONLINE_EMAIL_URL = r'https://api.mysubmail.com/mail/xsend'
ONLINE_EMAIL_APPID = "13955"
ONLINE_EMAIL_APPKEY = "2d21d55a5bdc018fbf7123544264dd9b"

# 自定义变量
CUSTOM_USER_LOGIN_URL = "/login"
CUSTOM_NOVEL_FILE_PATH = "f:/novels" if is_beta else "../novels"

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '"[%(asctime)s] [%(name)s] [%(levelname)s] : %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'fileStream': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, "novel_site.log"),
            'formatter': 'standard',
        },
        'standStream': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'default': {
            'handlers': ['fileStream', 'standStream'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

import logging

logger = logging.getLogger("default")

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}
