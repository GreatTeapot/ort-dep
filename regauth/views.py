from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import NotFound
# Create your views here.
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from ORT import settings
from .serializers import *
from .utils import refresh_access_token, set_auth_cookies, get_request_user


@extend_schema(tags=['Auth'])
class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = Response({
                'message': 'Registered',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            return set_auth_cookies(response, access_token, refresh_token)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Auth'])
class CustomUserLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        if not refresh_token:
            return Response({'error': 'Refresh token missing'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = refresh_access_token(refresh_token)
        if access_token:
            response = Response({'message': 'Access token refreshed successfully'}, status=status.HTTP_200_OK)
            return set_auth_cookies(response, access_token)

        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(tags=['Auth'])
class CustomUserList(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return get_request_user(self.request)


@extend_schema(tags=['Auth'])
class UserSearchList(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    lookup_field = 'id'

    def get_object(self):
        return get_request_user(self.request)


@extend_schema(tags=['Auth'])
class UserInfoAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return get_request_user(self.request)


@extend_schema(tags=['Auth'])
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = get_request_user(request)
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'detail': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Auth'])
class CustomUserTokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        if not refresh_token:
            return Response({'error': 'Refresh token missing'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = refresh_access_token(refresh_token)
        if access_token:
            response = Response({'message': 'Access token refreshed successfully'}, status=status.HTTP_200_OK)
            return set_auth_cookies(response, access_token)

        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)