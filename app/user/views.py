from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Token
from .serializers import (CreateUserSerializer, ListUserSerializer, AuthTokenSerializer,
                          CustomObtainTokenPairSerializer)

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class AuthViewsets(viewsets.ModelViewSet):
    """User viewsets"""
    queryset = get_user_model().objects.all()
    serializer_class = ListUserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['email', 'firstname', 'lastname', 'phone']
    ordering_fields = ['created_at', 'last_login',
                       'email', 'firstname', 'lastname', 'phone']

    def get_serializer_class(self):
        if self.action in ['create']:
            return CreateUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ['retrieve', 'list']:
            permission_classes = [AllowAny]
        elif self.action in ['destroy', 'partial_update']:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class CustomObtainTokenPairView(TokenObtainPairView):
    """Login with email and password"""
    serializer_class = CustomObtainTokenPairSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'created': created,
                'roles': user.roles
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
