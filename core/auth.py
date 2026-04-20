from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from django.contrib.auth.models import User
from ninja.security import HttpBearer
from ninja.errors import HttpError
from datetime import datetime, timedelta, timezone
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(user_id: int) -> str:
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': str(user_id),
        'exp': expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get('sub'))
    except JWTError:
        return None


class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        user_id = decode_access_token(token)
        if not user_id:
            raise HttpError(401, 'Invalid or expired token')
        try:
            user = User.objects.get(id=user_id)
            request.user = user
            return user
        except User.DoesNotExist:
            raise HttpError(401, 'User not found')