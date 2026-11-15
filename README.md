# GreenTech Analytics – Multi-Cloud Climate Data Service

A small REST service deployed on **AWS Lambda** and **Azure Functions** that combines
live weather (OpenWeatherMap) with historical temperature/CO₂ data (Kaggle Global Climate Change dataset).

`GET /climate?city=Pune` returns JSON: historical trend (warming °C/decade, CO₂ change, correlation),
live conditions, and the difference between today's temperature and the historical mean.

## Structure
- `aws_lambda/` – `lambda_function.py` + `processor.py` + CSV
- `azure_function/` – `function_app.py` (Python v2 model) + `processor.py` + CSV
- `scripts/benchmark.py` – concurrency/latency test, prints a markdown table
- `docs/REPORT.md` – report draft (fill in your metrics + screenshots)

## Prerequisites
Free-tier AWS and Azure accounts, Python 3.11+, a free OpenWeatherMap API key.
Replace `data/global_climate_sample.csv` with the real Kaggle file reduced to columns
`year,avg_temp_c,co2_ppm` (download from the Kaggle dataset page, then aggregate by year), and copy it into both function folders.

## Secrets
Never commit keys. Set env vars: `OWM_API_KEY` (required), `API_TOKEN` (optional bearer token).

## Deploy – AWS Lambda
1. Console → Lambda → Create function → Python 3.12, name `greentech-climate`.
2. Upload `aws_lambda/` contents as a zip (`cd aws_lambda && zip -r ../lambda.zip .`).
3. Configuration → Environment variables: add `OWM_API_KEY`.
4. Add an **API Gateway HTTP API** trigger (or a Function URL). For OAuth 2.0: create an Amazon Cognito user pool and attach a JWT authorizer to the route.
5. Test: `curl "https://<id>.execute-api.<region>.amazonaws.com/climate?city=Pune"`

## Deploy – Azure Functions
1. Install Azure Functions Core Tools and `az` CLI. `az login`.
2. Create a Function App (Python 3.11, Consumption plan, Linux).
3. `cd azure_function && func azure functionapp publish <APP_NAME>`
4. `az functionapp config appsettings set -n <APP_NAME> -g <RG> --settings OWM_API_KEY=<key>`
5. For OAuth 2.0: Function App → Authentication → add Microsoft Entra ID provider (Easy Auth).
6. Test: `curl "https://<APP_NAME>.azurewebsites.net/api/climate?city=Pune"`

Local run: `cd azure_function && func start`.

## Benchmark
```
python scripts/benchmark.py "<aws-url>" AWS --levels 1,5,10,25,50
python scripts/benchmark.py "<azure-url>" Azure --levels 1,5,10,25,50
```
Record the first (cold-start) request time separately, then paste both tables into the report.

## APIs used
| API | Use | Auth |
|---|---|---|
| OpenWeatherMap `/data/2.5/weather` | live temp, humidity, wind | API key (env var), HTTPS |
| Kaggle Global Climate Change dataset | historical temp + CO₂ (CSV) | Kaggle account download |
| AWS API Gateway / Azure HTTP trigger | public REST endpoint | OAuth 2.0 (Cognito / Entra ID) |
