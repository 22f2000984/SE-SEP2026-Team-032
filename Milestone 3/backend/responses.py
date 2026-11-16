"""Every error from the API has the same shape: {"error": "message"} with the right status code."""
from flask import jsonify, request


def error(message, status=400):
    return jsonify({"error": message}), status


def json_body():
    """The JSON object the client sent. Anything else (no body, a list, a number) counts as an empty object,
    so the field checks answer with a clear 400 instead of the server crashing."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}
