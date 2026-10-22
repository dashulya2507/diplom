from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ConfirmEmailToken, User
from .serializers import LoginSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)
        token = ConfirmEmailToken.objects.create(user=user, key=get_random_string(48))
        send_mail(
            'Подтверждение регистрации',
            f'Для подтверждения регистрации используйте токен: {token.key}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response({'Status': True, 'message': 'Письмо с подтверждением отправлено.'}, status=status.HTTP_201_CREATED)


class ConfirmEmailView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        key = request.data.get('token')
        token = ConfirmEmailToken.objects.filter(user__email=email, key=key).select_related('user').first()
        if not token:
            return Response({'Status': False, 'Error': 'Неверный email или токен.'}, status=status.HTTP_400_BAD_REQUEST)
        token.user.is_active = True
        token.user.save(update_fields=['is_active'])
        Token.objects.get_or_create(user=token.user)
        token.delete()
        return Response({'Status': True})


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if not user:
            return Response({'Status': False, 'Error': 'Неверный email или пароль.'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'Status': True, 'Token': token.key})


class MeView(APIView):
    def get(self, request):
        return Response({
            'id': request.user.id,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'type': request.user.type,
        })
