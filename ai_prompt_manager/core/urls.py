from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterUserView, CustomObtainAuthToken, PromptTemplateViewSet, PromptHistoryViewSet
from .views import generate_prompt_template

router = DefaultRouter()
router.register(r'prompts', PromptTemplateViewSet, basename='prompt')
router.register(r'history', PromptHistoryViewSet, basename='history')


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', CustomObtainAuthToken.as_view(), name='login'),
    path('generate/', generate_prompt_template, name='generate_prompt_template'),
    path('', include(router.urls)),
]