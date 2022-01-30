from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from email_validator import validate_email, EmailNotValidError
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Token, User
from .tasks import send_new_user_email


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'firstname', 'lastname', 'email', 'roles',
                  'image', 'verified', 'last_login', 'created_at']


class UserFollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'firstname', 'lastname', 'email']


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'password', 'firstname', 'lastname',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8},
                        'last_login': {'read_only': True}}

    def validate(self, attrs):
        email = attrs.get('email', None)
        if email:
            email = attrs['email'].lower().strip()
            if get_user_model().objects.filter(email=email).exists():
                raise serializers.ValidationError('Email already exists')
            try:
                valid = validate_email(attrs['email'])
                attrs['email'] = valid.email
                return super().validate(attrs)
            except EmailNotValidError as e:
                raise serializers.ValidationError(e)
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        token, _ = Token.objects.update_or_create(
            user=user, token_type='ACCOUNT_VERIFICATION',
            defaults={'user': user, 'token_type': 'ACCOUNT_VERIFICATION', 'token': get_random_string(120)})
        user_data = {'id': user.id, 'email': user.email, 'fullname': f"{user.lastname} {user.firstname}",
                     'url': f"{settings.CLIENT_URL}/verify-user/?token={token.token}"}
        send_new_user_email.delay(user_data)
        return user

    def update(self, instance, validated_data):
        # user = self.context['request'].user
        instance = super().update(instance, validated_data)
        if validated_data.get('password', False):
            instance.set_password(validated_data.get('password'))
            instance.save()
        return instance


class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        if not user.verified:
            raise exceptions.AuthenticationFailed(
                _('Account not yet verified.'), code='authentication')
        token = super().get_token(user)
        # Add custom claims
        token.id = user.id
        token['email'] = user.email
        token['roles'] = user.roles
        if user.firstname and user.lastname:
            token['fullname'] = user.firstname + ' ' + user.lastname
        if user.image:
            token['image'] = user.image.url
        token['phone'] = user.phone
        user.save_last_login()
        return token


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        if email:
            user = authenticate(
                request=self.context.get('request'),
                username=email.lower().strip(),
                password=password
            )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs
