from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-x1_1hta9k+_okr^g75r%#9o2$vs_uvqt)q)@h=i3u43b4zz8=6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.53.76','localhost','127.0.0.1','192.168.53.112','192.168.33.66','192.168.33.21','10.16.126.130','10.183.241.161']

SITE_DOMAIN = ''

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    #My Apps
    'shop',
    'copon2',
    'accaunts',
    'cart',
    'reservations',
    'siteinfo',
    'zarinpal',
    'django_apscheduler',
    'smartgtp',
    'django.contrib.sitemaps',
    'core',
    'sellers',
    'charts',
    'chat',
    'follow',
    'notifications',
    'question_response',
    'compare',
    'blog',
    'costs_fee',
    'facelogin',
    'walet',
    # 'opencv',
    'supporter',
    'watchlist',
    'gallery_products',
    'tiketing',
    'group_cart',
    'product_videos',
    'story',

    'shop_questions',
    'report_shop',
    'shop_coupon',
    'shop_manage_order',
    'shop_manage_products',
    'collaborator',
    'core_sellers',
    'response_tikets',
    # ----
    'adv',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #  کش وب سایت
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
]



ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',                
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'sellers.context_processors.default_shop_context', 
                'sellers.context_processors.shop_context',   
                'shop.context_processors.category_context',
                'cart.context_processors.quantityCart',
                'accaunts.context_processors.autheduser_context',   
                'sellers.context_processors.is_seller_context',    
                'siteinfo.context_processors.site_info_context',    
                'siteinfo.context_processors.website_seo',    
                'siteinfo.context_processors.symbol_of_trust_context',    
                'siteinfo.context_processors.top_brands',    
                'siteinfo.context_processors.promotional_card_product',    
                'costs_fee.context_processors.cost_fee_context', 
                'notifications.context_processors.unseenNotificaton_context',  
                'walet.context_processors.wallet_balance',  
                'collaborator.context_processors.count_shop_collaborators_context_processors',  
                'shop_questions.context_processors.count_shop_comments',  
                'shop_questions.context_processors.count_shop_questions',  
                'shop_questions.context_processors.count_shop_responses',  
                'gallery_products.context_processors.count_shop_gallery_context_processors',  
                'shop_manage_order.context_processors.count_shop_paid_reservs',  
                'shop_manage_order.context_processors.count_shop_send_reservs',  
                'shop_manage_order.context_processors.count_shop_unsend_reservs',  
                'shop_manage_order.context_processors.count_shop_canceled_reservs',  
                'shop_manage_order.context_processors.count_shop_today_reservs',  
                'shop_manage_products.context_processors.count_shop_products',  
                'shop_manage_products.context_processors.count_shop_lte2_products',
                'shop_coupon.context_processors.count_shop_coupons_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        },
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True


LOGIN_URL = '/accaunt/login/'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]



# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
import os

# MEDIA_URL = 'media/'
MEDIA_URL = 'MEDIA/'

MEDIA_ROOT = os.path.join(BASE_DIR,'media')




EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'alakalashop@gmail.com'
EMAIL_HOST_PASSWORD = 'vxwv xfkt ahme vfyz '
ADMIN_GMAIL = 'alakala@gmail.com'



# کش سایت
# CACHE_MIDDLEWARE_SECONDS = 86400  # یک روز
# CACHE_MIDDLEWARE_ALIAS = 'default'
# CACHE_MIDDLEWARE_KEY_PREFIX = ''





JAZZMIN_SETTINGS = {
    "site_title": "پنل مدیریت من",
    "site_header": "مدیریت Alastra",
    "site_brand": "Alastra",
    "welcome_sign": "به پنل مدیریت خوش آمدید",
    "show_sidebar": True,
    "dark_mode": True,
}

APSCHEDULER_JOBSTORES = {
    'default': {
        'class': 'apscheduler.jobstores.memory:MemoryJobStore'
    }
}



# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }


from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'monthly-profit-task': {
        'task': 'charts.tasks.monthly_job',
        'schedule': crontab(minute=59, hour=12, day_of_month=1),  
    },
    'price-history-task': {
        'task': 'charts.tasks.monthly_price_history_job',
        'schedule': crontab(minute=30, hour=12, day_of_month=1),  
    },
    'start-sent-notification-task': {
        'task': 'notifications.tasks.start_sent_notifications',
        'schedule': crontab(hour=20),   
    },
    'start-runing-functions-task': {
        'task': 'notifications.tasks.start_runing_functions',
        'schedule': crontab(hour=23),  
    },
    'disactive-history-task': {
        'task': 'story.tasks.default_disactive_history',
        'schedule': crontab(hour=23),  
    },
    'report-shops-task': {
        'task': 'report_shop.tasks.report_counts',
        'schedule': crontab(hour=23),  
    },
}