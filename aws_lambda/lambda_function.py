import json, os
from processor import build_response

HISTORY = os.path.join(os.path.dirname(__file__), "global_climate_sample.csv")


def _resp(code, body):
    return {"statusCode": code, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(body)}


def lambda_handler(event, context):
    # OAuth 2.0 / JWT is enforced by the API Gateway authorizer (Cognito) in front of this function.
    # Optional extra guard for the prototype: static bearer token from env.
    token = os.environ.get("API_TOKEN")
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    if token and headers.get("authorization") != f"Bearer {token}":
        return _resp(401, {"error": "unauthorized"})
    city = (event.get("queryStringParameters") or {}).get("city", "London")
    try:
        return _resp(200, build_response(city, os.environ.get("OWM_API_KEY"), HISTORY, "aws-lambda"))
    except Exception as e:  # keep errors JSON, never leak keys
        return _resp(502, {"error": type(e).__name__})