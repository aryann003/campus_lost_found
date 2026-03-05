from .base import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'aryankatiyar642@gmail.com'
EMAIL_HOST_PASSWORD = 'xisf atke qvqf lndw'
DEFAULT_FROM_EMAIL = 'Campus LostFound <aryankatiyar642@gmail.com>' 