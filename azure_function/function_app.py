import json, os
import azure.functions as func
from processor import build_response

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)  # auth via Entra ID Easy Auth (OAuth 2.0)
HISTORY = os.path.join(os.path.dirname(__file__), "global_climate_sample.csv")


@app.route(route="climate", methods=["GET"])
def climate(req: func.HttpRequest) -> func.HttpResponse:
    token = os.environ.get("API_TOKEN")
    if token and req.headers.get("Authorization") != f"Bearer {token}":
        return func.HttpResponse(json.dumps({"error": "unauthorized"}), status_code=401,
                                 mimetype="application/json")
    city = req.params.get("city", "London")
    try:
        body = build_response(city, os.environ.get("OWM_API_KEY"), HISTORY, "azure-functions")
        return func.HttpResponse(json.dumps(body), mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": type(e).__name__}), status_code=502,
                                 mimetype="application/json")