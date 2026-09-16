from datetime import datetime, timedelta, timezone

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User
from jose import jwt, JWTError
from ninja.security import HttpBearer
from ninja.errors import HttpError
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # Allow tests to run without a real SECRET_KEY by falling back to a
    # deterministic sentinel. Outside of the test runner, raise immediately
    # so misconfigured deployments fail fast at startup.
    if getattr(django_settings, '_running_tests', False):
        SECRET_KEY = 'test-only-insecure-secret-key'
    else:
        raise ImproperlyConfigured(
            'SECRET_KEY environment variable is required for JWT authentication.'
        )

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(user_id):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': str(user_id),
        'exp': expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get('sub'))
    except JWTError:
        return None


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        user_id = decode_access_token(token)
        if not user_id:
            raise HttpError(401, 'Invalid or expired token')
        try:
            user = User.objects.get(id=user_id)
            request.user = user
            return user
        except User.DoesNotExist:
            raise HttpError(401, 'User not found')