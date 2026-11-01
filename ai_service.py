import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Synthetic samples only. Do not replace these with Telegram-derived content
# unless Telegram has granted an applicable exception for the specific scope.
SAMPLES = {
    "urgent_complaint": {
        "label": "Urgent customer complaint",
        "message": "My order arrived damaged, and I need a replacement before tomorrow.",
    },
    "sales_lead": {
        "label": "Potential sales lead",
        "message": "I want to purchase 50 units. Please share your wholesale price.",
    },
    "general_enquiry": {
        "label": "General enquiry",
        "message": "Do you have this product available in blue?",
    },
}


def get_samples():
    return SAMPLES


def analyze_sample(sample_key):
    if sample_key not in SAMPLES:
        raise ValueError("Please select a valid demo message.")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from your .env file.")

    sample_message = SAMPLES[sample_key]["message"]
    prompt = f"""
You classify synthetic sample messages for a business inbox. This is invented
sample text and is not taken from a messaging platform or a real customer.
Return only JSON with keys:
priority (HIGH, MEDIUM or LOW), score (integer 0-100), category,
reason (one sentence), suggested_reply (short, polite reply draft).
Prioritize urgent complaints and deadlines; treat concrete sales opportunities
as important. Do not invent order details or promise actions that are unknown.

Sample message:
{sample_message}
"""

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            max_output_tokens=400,
        ),
    )

    try:
        data = json.loads(response.text or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError("Gemini did not return valid JSON. Please try again.") from exc

    priority = str(data.get("priority", "")).upper()
    if priority not in {"HIGH", "MEDIUM", "LOW"}:
        raise ValueError("Gemini returned an invalid priority. Please try again.")

    try:
        score = max(0, min(100, int(data.get("score", 0))))
    except (TypeError, ValueError) as exc:
        raise ValueError("Gemini returned an invalid score.") from exc

    return {
        "message": sample_message,
        "priority": priority,
        "score": score,
        "category": str(data.get("category", "General")),
        "reason": str(data.get("reason", "No reason supplied.")),
        "suggested_reply": str(data.get("suggested_reply", "")),
    }
