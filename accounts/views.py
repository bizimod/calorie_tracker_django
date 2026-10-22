from rest_framework.response import Response
from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action

from .models import Profile
from .serializers import ProfileSerializer, RegisterSerializer


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
