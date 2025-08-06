
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
from core.ai.utils import analyze_prompt_with_ai

import json
import openai

from rest_framework.decorators import api_view, permission_classes

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
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
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


client = OpenAI(api_key=settings.OPENAI_API_KEY)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_prompt_template(request):
    try:
        user = request.user
        intent = request.data.get("intent")
        attributes = request.data.get("attributes", {})

        if not intent:
            return Response({"error": "Intent is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Format the GPT prompt
        prompt_input = build_structured_prompt(intent, attributes)

        # Step 2: Call GPT to generate structured prompt
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a prompt generator that creates clear, concise prompts for various AI tasks."},
                {"role": "user", "content": prompt_input}
            ],
            temperature=2,
            max_tokens=300
        )

        generated_prompt = response.choices[0].message.content.strip()

        # Step 3: Get AI feedback/clarity score
        analysis = analyze_prompt_with_ai(generated_prompt)

        # Step 4: Save the new PromptTemplate
        prompt_instance = PromptTemplate.objects.create(
            user=user,
            prompt_title=f"Generated Prompt: {intent[:50]}",
            content=generated_prompt,
            category=analysis.get("category", "other") if analysis else "other",
            priority=analysis.get("priority", "low") if analysis else "low",
            clarity_score=analysis.get("clarity_score") if analysis else None,
            ai_feedback=analysis.get("ai_feedback") if analysis else None,
        )

        return Response({
            "template_id": prompt_instance.id,
            "prompt": generated_prompt,
            "clarity_score": prompt_instance.clarity_score,
            "ai_feedback": prompt_instance.ai_feedback,
            "status": "success"
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def build_structured_prompt(intent, attributes):
    """
    Constructs the GPT input to generate a usable AI prompt from user intent and attributes.
    """
    examples = f"""
                    [Instruction]
                    You are a prompt generator AI. Based on user intent and a few attributes, generate a clear, effective prompt for an AI model.

                    The final prompt should:
                    - Be concise
                    - Cover the intent clearly
                    - Respect any parameters (like tone, format, answer type)
                    - Be ready to use in a model like ChatGPT

                    [Input]
                    Intent: I want to write ad copy for a fitness product
                    Attributes: {{"tone": "motivational", "target_audience": "young adults"}}
                    [Output]
                    Write a motivational ad copy for a fitness product targeting young adults.

                    [Input]
                    Intent: I want to design an email campaign
                    Attributes: {{"tone": "professional", "goal": "boost conversions"}}
                    [Output]
                    Write a professional email campaign that boosts conversions.

                    [Input]
                    Intent: {intent}
                    Attributes: {json.dumps(attributes)}
                    [Output]
                    """
    return examples.strip()