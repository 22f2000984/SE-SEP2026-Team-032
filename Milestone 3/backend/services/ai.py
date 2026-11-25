"""The one place that talks to OpenAI. Both AI features (Smart Match and Pulse review) call ask_json().
It returns a dictionary, or None when there is no key or anything goes wrong. The callers then use their simple rules,
so the platform keeps working without the AI."""
import json
import urllib.request

from flask import current_app

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def ai_is_on():
    return bool(current_app.config["OPENAI_API_KEY"])


def ask_json(instructions, data):
    """Sends the instructions and the data (a dictionary) to OpenAI and returns the JSON answer as a dictionary, or None."""
    if not ai_is_on():
        return None
    payload = {
        "model": current_app.config["OPENAI_MODEL"],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": json.dumps(data)},
        ],
    }
    request = urllib.request.Request(
        OPENAI_URL, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Authorization": "Bearer " + current_app.config["OPENAI_API_KEY"], "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            reply = json.loads(response.read().decode("utf-8"))
        answer = json.loads(reply["choices"][0]["message"]["content"])
    except Exception:  # no network, wrong key, bad JSON...
        return None
    return answer if isinstance(answer, dict) else None
