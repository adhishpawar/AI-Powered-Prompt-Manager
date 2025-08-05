from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import PromptTemplate
from ai.utils import analyze_prompt_with_ai

import logging
logger = logging.getLogger(__name__)

print("✅ signals.py loaded")
logger.info("✅ signals.py loaded")


@receiver(post_save, sender=PromptTemplate)
def auto_classify_prompt(sender, instance, created, **kwargs):
    if created:
        result = analyze_prompt_with_ai(instance.content)
        print("AI Result from OpenAI:", result)
        logger.info(f"AI Result from OpenAI: {result}") 

        if result:
            PromptTemplate.objects.filter(pk=instance.pk).update(
                category=result["category"],
                priority=result["priority"],
                clarity_score=result["clarity_score"],
                ai_feedback=result["ai_feedback"]
            )

