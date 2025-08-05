from django.db import models
from django.contrib.auth.models import User


class PromptTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompts')
    prompt_title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.CharField(max_length=50, default='general') 
    visibility = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)   #Now Added

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class PromptHistory(models.Model):
    prompt = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE, related_name='histories')
    input_data = models.TextField(blank=True, null=True)
    openai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for Prompt ID {self.prompt.id} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
