
from rest_framework import generics
from rest_framework import filters
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated

from .models import PromptTemplate, PromptHistory
from .serializers import PromptTemplateSerializers, PromptHistorySerializer

from openai import OpenAI
from django.conf import settings


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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    
    def get_queryset(self):
        return PromptTemplate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def run(self, request, pk = None):
        try:
            print("🔍 Starting /run/ logic")
            prompt_obj = self.get_object()
            input_data = request.data.get('input', '')
            full_prompt = f"{prompt_obj.content}\n{input_data}"
            print(f"📥 Input Data: {input_data}")

            full_prompt = f"{prompt_obj.content}\n{input_data}"
            print(f"🧠 Full Prompt: {full_prompt}")


            #OpenAI CALL
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=100
            )


            print("✅ OpenAI API call successful")

            output = response.choices[0].message.content.strip()


            #save in PromptHistory
            PromptHistory.objects.create(
                prompt = prompt_obj,
                input_data = input_data,
                openai_response = output
            )

            print("💾 History saved")

            return Response({'output':output}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("❌ ERROR:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class PromptHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = PromptHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PromptHistory.objects.filter(prompt__user=self.request.user)