# URL Shortener — Production-Grade Microservices

A production-grade URL shortener built as a learning project covering **microservices**, **message queues**, **caching**, **Kubernetes**, and **AWS**.

## Architecture

```
Client → URL Service (FastAPI + Redis) → SQS → Analytics Service (Node.js + Postgres)
```

| Service | Stack | Port |
|---|---|---|
| URL Service | Python FastAPI + Redis | 8000 |
| Analytics Service | Node.js + PostgreSQL | 3000 |

## Tech Stack

- **URL Service**: FastAPI, Redis (caching), PostgreSQL, Docker
- **Analytics Service**: Node.js, AWS SQS, PostgreSQL
- **Infra**: Docker Compose (local), Kubernetes (minikube), AWS (EC2 + RDS + SQS + ElastiCache)
- **CI/CD**: GitHub Actions

## Quick Start (Local)

```bash
# 1. Clone
git clone <your-repo>
cd url-shortener

# 2. Copy env files
cp url-service/.env.example url-service/.env
cp analytics-service/.env.example analytics-service/.env

# 3. Start all services
docker compose up --build

# 4. Test it
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

# Visit http://localhost:8000/{short_code} — you'll be redirected
# Visit http://localhost:3000/analytics/{short_code} — see click stats
```

## Project Structure

```
url-shortener/
├── url-service/          # Python FastAPI — shorten & redirect
├── analytics-service/    # Node.js — click event consumer
├── k8s/                  # Kubernetes manifests
├── docker/               # Shared docker configs
├── .github/workflows/    # CI/CD pipelines
└── docker-compose.yml
```

## Learning Checkpoints

- [ ] Day 1-2: URL Service working locally
- [ ] Day 3-4: Analytics Service + SQS via LocalStack
- [ ] Day 5: Full Docker Compose flow
- [ ] Day 6-7: Kubernetes on minikube
- [ ] Day 8-9: Deploy to AWS EC2
- [ ] Day 10: GitHub Actions CI/CD

## Architecture Decisions

**Why SQS instead of direct HTTP?**
Click tracking is non-critical and high-volume. Making the URL redirect wait for analytics to write to DB would add latency. SQS decouples them — redirect is instant, analytics catch up async.

**Why Redis for URL lookups?**
Every redirect hits the same DB row for popular URLs. Redis caches the mapping so we skip the DB entirely after the first hit. Sub-millisecond vs ~10ms.

**Why two separate services?**
They have different scaling needs. URL service handles spiky redirect traffic. Analytics service processes a steady queue. Independent deployment, independent scaling.
