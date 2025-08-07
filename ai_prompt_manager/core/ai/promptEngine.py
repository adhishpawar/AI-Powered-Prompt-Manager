import openai

import logging
intent_logger = logging.getLogger("intent_logger")



def expand_intent(intent: str) -> str:
    """
    Uses OpenAI API to take a vague user intent and return a clearer, expanded version.
    Only returns a refined prompt string (no JSON or metadata).
    """

    prompt = f"""
    The user said: "{intent}"
    
    Your task is to interpret and rephrase this as a clear, specific, expanded prompt that is ready for an AI assistant to understand.
    
    Only output the improved prompt.
    Do NOT include any explanation, attributes, or metadata.
    
    Examples:

    Input: "I want to write a blog"
    Output: "Write a comprehensive blog post about a trending topic that engages readers and drives traffic."

    Input: "Create a report"
    Output: "Generate a detailed business report summarizing quarterly financial performance."

    Now expand this intent: "{intent}"
    """

    

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a prompt rewriter that turns vague ideas into clear and specific AI-ready prompts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=100
    )

    expanded_prompt = response.choices[0].message.content.strip()

    intent_logger.info(f"Original intent: {intent} | Expanded: {expanded_prompt}")

    return expanded_prompt
