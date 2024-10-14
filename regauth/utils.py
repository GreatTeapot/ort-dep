from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import RefreshToken

from ORT import settings


def get_request_user(request):
    user = request.user
    if not user:
        raise NotFound(detail="User not found.")
    return user

def set_auth_cookies(response, access_token, refresh_token=None):
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        value=access_token,
        httponly=True,
        secure=False,
        samesite='Lax',
    )
    if refresh_token:
        response.set_cookie(
            key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='Lax',
        )
    return response


def refresh_access_token(refresh_token):
    try:
        token = RefreshToken(refresh_token)
        return str(token.access_token)
    except Exception:
        return None