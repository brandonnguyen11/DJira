from groq import Groq
import os
import json
import re

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_ticket_data(context: dict, extra_context: str = "") -> dict:
    prompt = f"""
You are a project manager converting a Discord message into a Jira ticket.
Respond with a raw JSON object only — no markdown, no code fences.

Discord channel: {context['channel_name']}
Author: {context['author']}
Message:
{context['raw']}
{"Extra context: " + extra_context if extra_context else ""}
Source link: {context['source_url']}

Return this JSON shape:
{{
  "summary": "Short ticket title (max 100 chars)",
  "description": "Detailed description including the source Discord link",
  "issueType": "Task | Bug | Story",
  "priority": "High | Medium | Low"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Groq returned invalid JSON: {text[:200]}")