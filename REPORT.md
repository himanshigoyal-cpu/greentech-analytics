# GreenTech Analytics: Multi-Cloud Climate Data Service
*Cloud Development – Introduction to Cloud Computing, Modular Assignment 1*
**Name:** ______  **Repo:** <GitHub link>  **AWS URL:** <link>  **Azure URL:** <link>

## 1. Introduction
GreenTech Analytics needs a sustainable, low-overhead data processing service. I built a prototype REST API that merges live weather from OpenWeatherMap with historical temperature and CO₂ records from Kaggle's Global Climate Change dataset, and deployed the same logic on AWS Lambda and Azure Functions to compare the two platforms.

## 2. Architecture
```
 Client (browser / curl)
        │  HTTPS + OAuth 2.0 bearer token
        ▼
 ┌───────────────────┐          ┌────────────────────┐
 │ API Gateway +     │          │ Azure HTTP trigger │
 │ Cognito authorizer│          │ + Entra ID auth    │
 └─────────┬─────────┘          └─────────┬──────────┘
           ▼                              ▼
 ┌───────────────────┐          ┌────────────────────┐
 │  AWS Lambda       │          │  Azure Function    │
 │  (processor.py)   │          │  (processor.py)    │
 └───┬───────────┬───┘          └───┬────────────┬───┘
     │           │                  │            │
     ▼           ▼                  ▼            ▼
 OpenWeatherMap  Historical CSV   OpenWeatherMap  Historical CSV
 (live, REST)    (Kaggle)         (live, REST)    (Kaggle)
```
*(Redraw this in draw.io/Lucidchart for the final submission if you prefer.)*

## 3. NIST Cloud Model Mapping (Task 1)
**Essential characteristics**
- **On-demand self-service:** functions and endpoints provisioned from consoles/CLI without provider interaction.
- **Broad network access:** consumed over HTTPS by any client using REST/JSON.
- **Resource pooling:** Lambda and Functions run on shared multi-tenant infrastructure; I do not manage servers.
- **Rapid elasticity:** both platforms add concurrent instances automatically under load (shown in Section 6).
- **Measured service:** CloudWatch and Application Insights report invocations, duration and cost; billing is per execution.

**Service model:** FaaS, which is a serverless form of PaaS. The provider manages OS and runtime; I manage code and configuration.
**Deployment model:** public cloud (two providers), giving a multi-cloud setup.

## 4. Implementation (Tasks 2 & 3)
A shared `processor.py` (standard library only) does three things: calls OpenWeatherMap over HTTPS and parses JSON; loads the historical CSV and computes mean temperature, warming rate per decade (linear regression), CO₂ change and temperature–CO₂ correlation; and returns a combined JSON response including the live-versus-historical temperature gap. Thin provider-specific wrappers (`lambda_function.py`, `function_app.py`) handle the HTTP event format, which keeps the business logic portable and makes the comparison fair.

Security: HTTPS only; API keys held in environment variables, never in code; OAuth 2.0 via a Cognito JWT authorizer (AWS) and Entra ID Easy Auth (Azure); errors return generic JSON so secrets are never leaked. Open standards: REST, JSON, OAuth 2.0.

*Screenshots to add: (a) AWS Lambda console, (b) Azure Function app, (c) successful curl output from each, (d) environment variable pages with values hidden.*

## 5. Scalability & Performance (Task 4)
Method: `scripts/benchmark.py` sent 4×N requests at concurrency N ∈ {1, 5, 10, 25, 50} to each endpoint after one warm-up call.

| Metric | AWS Lambda | Azure Functions |
|---|---|---|
| Cold start (first request) | __ ms | __ ms |
| Avg latency @ 1 | __ | __ |
| Avg latency @ 10 | __ | __ |
| p95 latency @ 50 | __ | __ |
| Errors @ 50 | __ | __ |
| Max throughput (req/s) | __ | __ |
| Est. cost per 1M requests | ~$0.20 + compute | ~$0.20 + compute |

*Add a latency-vs-concurrency chart. Discuss: did latency stay flat as concurrency rose (elasticity)? Did either platform throttle or cold-start more?*

## 6. Provider Comparison (Task 5)
**AWS Lambda – advantages:** fast cold starts for light Python, very mature ecosystem, simple API Gateway integration, generous free tier. **Limitations:** API Gateway/IAM/Cognito setup has a steeper learning curve; logs live in a separate service (CloudWatch).
**Azure Functions – advantages:** excellent local tooling (`func start`) and one-command deploy from Core Tools, built-in Application Insights, Easy Auth makes OAuth fast to enable. **Limitations:** Consumption-plan cold starts can be longer, and portal/resource-group concepts add initial overhead.
*Replace with your own measured observations; markers will reward evidence over generic claims.*

## 7. Conclusion
Keeping logic provider-agnostic made multi-cloud deployment cheap, and serverless elasticity suits spiky, small-dataset climate analytics. Future work: cache OpenWeatherMap responses, store history in S3/Blob Storage, add scheduled ingestion.
