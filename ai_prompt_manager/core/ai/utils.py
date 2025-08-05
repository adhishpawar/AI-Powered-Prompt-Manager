from openai import OpenAI 
import logging
import json
import re
from django.conf import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)
MODEL = "gpt-4o"

def analyze_prompt_with_ai(prompt_text):
    """
    Evaluates a prompt using OpenAI API and returns a dictionary with:
    category, priority, clarity_score, ai_feedback
    """
    system_message = {
        "role": "system",
        "content": (
            "You are an expert AI prompt evaluator. "
            "Classify user prompts, assess their complexity, clarity, and provide short feedback."
        )
    }

    user_message = {
        "role": "user",
        "content": f"""
                        Analyze the following prompt and return a JSON object with:
                        - category: One of ["Business", "Tech", "Education", "Healthcare", "Design", "Other"]
                        - priority: One of ["Low", "Medium", "High"]
                        - clarity_score: A number between 1 and 10
                        - ai_feedback: One-sentence feedback

                        Prompt: \"\"\"{prompt_text}\"\"\"
                    """
    }

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[system_message, user_message],
            temperature=0.3,
            max_tokens=300,
            timeout=10,
        )

        raw = response.choices[0].message.content
        logger.info(f"AI Raw Output: {raw}")

        json_data = extract_json(raw)
        if not json_data:
            logger.error("Could not extract JSON from AI response.")
            return None

        return {
            "category": json_data.get("category", "Other").lower(),
            "priority": json_data.get("priority", "Low").lower(),
            "clarity_score": float(json_data.get("clarity_score", 0)),
            "ai_feedback": json_data.get("ai_feedback", "").strip(),
        }

    except Exception as e:
        logger.error(f"[OpenAI API Error]: {e}")
        return None

def extract_json(text):
    """
    Extracts JSON object from messy text using regex.
    """
    try:
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        logger.error(f"JSON Extraction Error: {e}")
    return None
