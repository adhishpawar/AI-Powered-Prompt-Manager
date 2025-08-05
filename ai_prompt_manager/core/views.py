
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

import logging
prompt_logger = logging.getLogger('prompt_logger')


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
        instance = serializer.save(user=self.request.user)

        from core.ai.utils import analyze_prompt_with_ai
        result = analyze_prompt_with_ai(instance.content)

        if result:
            instance.category = result["category"]
            instance.priority = result["priority"]
            instance.clarity_score = result["clarity_score"]
            instance.ai_feedback = result["ai_feedback"]
            instance.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def run(self, request, pk = None):
        try:
           
            prompt_obj = self.get_object()
            input_data = request.data.get('input', '')
            full_prompt = f"{prompt_obj.content}\n{input_data}"

            # LOG the prompt and input
            prompt_logger.info(f"[{request.user.username}] Prompt: {prompt_obj.content} | Input: {input_data}")

            #OpenAI CALL
            
            openai.api_key = settings.OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=100
            )

            output = response.choices[0].message.content

            # LOG the output
            prompt_logger.info(f"[{request.user.username}] OpenAI Output: {output}")


            #save in PromptHistory
            PromptHistory.objects.create(
                prompt = prompt_obj,
                input_data = input_data,
                openai_response = output
            )

            return Response({'output':output}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("ERROR:", str(e))
            prompt_logger.error(f"Error while processing prompt: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class PromptHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = PromptHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PromptHistory.objects.filter(prompt__user=self.request.user)