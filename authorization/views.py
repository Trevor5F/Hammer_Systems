from .models import User, InvitedUser
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
import string
import random
import time


class PhoneNumberAuthView(CreateAPIView):
    model = User
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        # Проверяем, был ли уже отправлен код авторизации для этого номера телефона
        if User.objects.filter(phone_number=phone_number, auth_code__isnull=False).exists():
            return Response({'error': 'Код авторизации уже отправлен на этот номер телефона.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Имитация отправки 4-значного кода авторизации с задержкой 1-2 секунды
        time.sleep(random.randint(1, 2))
        auth_code = ''.join(random.choices(string.digits, k=4))
        invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        # Создаём нового пользователя
        user = User(phone_number=phone_number, auth_code=auth_code, invite_code=invite_code)
        user.save()

        # Возвращаем пользователю код авторизации, чтобы он мог подтвердить его
        return Response({'auth_code': auth_code, 'message': 'Код авторизации отправлен на номер телефона.'},
                        status=status.HTTP_200_OK)


class AuthCodeCheckView(UpdateAPIView):
    model = User
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        auth_code = request.data.get('auth_code')

        try:
            user = User.objects.get(phone_number=phone_number, auth_code=auth_code)
            # Очистить код авторизации после успешной проверки
            user.auth_code = ''
            user.save()
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Неверный код авторизации или номер телефона'}, status=400)


class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(self.get_queryset(), pk=user_id)

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        invite_code = request.data.get('invite_code')

        if user.auth_code:
            return Response({'error': 'Вы не авторизованы. Пожалуйста, подтвердите код авторизации.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if user.activated_invite_code:
            return Response({'error': 'Инвайт-код уже активирован.'}, status=status.HTTP_400_BAD_REQUEST)

        if invite_code:  # Если пользователь ввел инвайт-код
            if User.objects.filter(invite_code=invite_code).exists():
                # Проверяем, является ли введенный инвайт-код чужим
                if invite_code != user.invite_code:
                    # Если инвайт-код чужой, то просто активируем его, не обновляя свой собственный инвайт-код
                    user.activated_invite_code = True
                    user.save()
                    # Сохраняем информацию о том, что пользователь ввел чужой инвайт-код
                    invited_user = InvitedUser(user=user, invited_by=User.objects.get(invite_code=invite_code))
                    invited_user.save()
                else:
                    # Если инвайт-код совпадает с собственным, выдаем ошибку
                    return Response({'error': 'Вы не можете использовать собственный инвайт-код.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'Инвайт-код успешно активирован.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Неверный инвайт-код.'}, status=status.HTTP_400_BAD_REQUEST)
        else:  # Если пользователь не ввел инвайт-код, просто возвращаем профиль
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        invited_users = InvitedUser.objects.filter(invited_by=user)
        phone_numbers = [invited_user.user.phone_number for invited_user in invited_users]
        return Response(phone_numbers, status=status.HTTP_200_OK)
