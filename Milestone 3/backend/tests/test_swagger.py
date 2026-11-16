"""The Swagger file must be valid and must describe every route the app really has (and nothing more)."""
import os
import re

import yaml
from openapi_spec_validator import validate

SWAGGER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "swagger.yaml")
METHODS = ("get", "post", "put", "patch", "delete")


def load_spec():
    with open(SWAGGER) as f:
        return yaml.safe_load(f)


def documented_operations(spec):
    return {(method.upper(), path) for path, item in spec["paths"].items() for method in item if method in METHODS}


def real_operations(app):
    found = set()
    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        path = re.sub(r"<(?:int:)?(\w+)>", r"{\1}", rule.rule)
        for method in rule.methods - {"HEAD", "OPTIONS"}:
            found.add((method, path))
    return found


def test_swagger_file_is_valid_openapi():
    validate(load_spec())


def test_every_route_is_documented_and_nothing_extra(client):
    from flask import current_app
    assert real_operations(current_app) == documented_operations(load_spec())


def test_every_operation_lists_its_user_stories_or_is_general():
    spec = load_spec()
    for path, item in spec["paths"].items():
        for method in item:
            if method in METHODS and path not in ("/api/health",):
                assert item[method].get("x-user-stories"), f"{method.upper()} {path} has no x-user-stories"
