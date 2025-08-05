
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PromptTemplate, PromptHistory
from .serializers import PromptTemplateSerializers, PromptHistorySerializer


##Registration View
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=response.data['username'])
        token, created  = Token.objects.get_or_create(user = user)
        return Response({
            'user' : response.data,
            'token' : token.key
        })
    

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key = response.data['token'])
        return Response({
            'token': token.key,
            'username': token.user.username
        })
    

class PromptTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = PromptTemplateSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PromptTemplate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PromptHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = PromptHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PromptHistory.objects.filter(prompt__user=self.request.user)