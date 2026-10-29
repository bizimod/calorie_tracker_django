from rest_framework.response import Response
from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework_simplejwt.exceptions import TokenError

from .models import Profile
from .serializers import ProfileSerializer, RegisterSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class ProfileViewSet(viewsets.GenericViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'patch', 'put'])
    def me(self, request):
        profile = request.user.profile
        if request.method in ('PATCH', 'PUT'):
            serializer = self.get_serializer(
                profile,
                data=request.data,
                partial=(request.method == 'PATCH'),
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(self.get_serializer(profile).data)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'detail': 'Поле refresh обязательно'}, status=400)
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response({'detail': 'Неверный или истёкший токен'}, status=400)
        return Response(status=204)