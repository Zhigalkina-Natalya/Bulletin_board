from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import ChangePasswordSerializer, MyTokenObtainPairSerializer, UserRegisterSerializer, UserSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ProfileView(RetrieveUpdateAPIView):
    """
    Профиль пользователя:
    - GET -> получить свои данные
    - PUT/PATCH -> обновить свои данные
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Возвращает текущего пользователя."""
        return self.request.user


class RegisterView(CreateAPIView):
    """Регистрация пользователя."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer


class ChangePasswordView(APIView):
    """Смена пароля пользователя."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response({"detail": "Пароль успешно изменен"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
