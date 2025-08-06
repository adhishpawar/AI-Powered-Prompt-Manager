from django.db import models
from django.contrib.auth.models import User


class PromptTemplate(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('marketing', 'Marketing'),
        ('educational', 'Educational'),
        ('design', 'Design'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompts')
    prompt_title = models.CharField(max_length=100)
    content = models.TextField()

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        null=False,
        blank=False,
        help_text="AI-assigned category (e.g., Technical, Marketing, Educational)"
    ) 

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='low',
        null=False,
        blank=False,
        help_text="AI-evaluated priority level"
    )

    clarity_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="AI-evaluated clarity score (1.00 to 10.00)"
    )

    ai_feedback = models.TextField(
        null=True,
        blank=True,
        help_text="AI-generated suggestions or review comments for this prompt"
    )

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Prompt Template"
        verbose_name_plural = "Prompt Templates"

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class PromptHistory(models.Model):
    prompt = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE, related_name='histories')
    input_data = models.TextField(blank=True, null=True)
    openai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for Prompt ID {self.prompt.id} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
class PromptIntent(models.Model):
    STAGE_CHOICES = [
        ('draft', 'Draft'),
        ('clarifying', 'Clarifying'),
        ('finalized', 'Finalized')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='intents')
    intent = models.TextField(help_text="User's raw prompt idea")
    clarification_chat = models.TextField(blank=True, null=True, help_text="Running chat history with GPT")
    structured_prompt = models.TextField(blank=True, null=True, help_text="Final refined prompt from GPT")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Intent by {self.user.username} - {self.stage}"
