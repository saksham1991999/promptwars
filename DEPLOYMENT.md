# Chess Alive - Production Deployment Guide

Complete step-by-step guide for deploying Chess Alive to Google Cloud Run.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment](#post-deployment)
- [Monitoring](#monitoring)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts & Services
- [ ] Google Cloud Platform account with billing enabled
- [ ] Supabase production project created
- [ ] Redis instance (Google Memorystore or external)
- [ ] Sentry project for error tracking
- [ ] PostHog project for analytics
- [ ] GitHub repository with Actions enabled

### Required Tools
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install Docker
# https://docs.docker.com/get-docker/

# Verify installations
gcloud --version
docker --version
```

---

## Initial Setup

### 1. Configure Google Cloud Project

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

### 2. Create Service Account

```bash
# Create service account for Cloud Run
gcloud iam service-accounts create chess-alive-sa \
  --display-name="Chess Alive Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:chess-alive-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# For CI/CD: create key for GitHub Actions
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=chess-alive-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com

# Add this key to GitHub Secrets as GCP_SA_KEY
```

### 3. Store Secrets in Secret Manager

```bash
# Backend secrets
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create chess-alive-secret-key --data-file=-

echo -n "https://your-project.supabase.co" | \
  gcloud secrets create chess-alive-supabase-url --data-file=-

echo -n "your-supabase-service-role-key" | \
  gcloud secrets create chess-alive-supabase-secret --data-file=-

echo -n "your-gemini-api-key" | \
  gcloud secrets create chess-alive-gemini-key --data-file=-

echo -n "redis://your-redis:6379" | \
  gcloud secrets create chess-alive-redis-url --data-file=-

echo -n "https://your-sentry-dsn" | \
  gcloud secrets create chess-alive-sentry-dsn --data-file=-

echo -n "your-posthog-key" | \
  gcloud secrets create chess-alive-posthog-key --data-file=-
```

### 4. Setup Redis (Google Memorystore)

```bash
# Create Redis instance
gcloud redis instances create chess-alive-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0 \
  --tier=basic

# Get connection info
gcloud redis instances describe chess-alive-redis \
  --region=us-central1 \
  --format="value(host)"
```

### 5. Configure GitHub Secrets

Add these secrets to your GitHub repository:
- `GCP_SA_KEY` - Service account JSON key
- `GCP_PROJECT_ID` - Your GCP project ID
- `SUPABASE_URL` - Production Supabase URL
- `SUPABASE_PUBLISHABLE_KEY` - Supabase anon key
- `POSTHOG_API_KEY` - PostHog project key
- `SENTRY_DSN_FRONTEND` - Sentry DSN for frontend

---

## Deployment Steps

### Option 1: Deploy via GitHub Actions (Recommended)

1. **Push to main branch:**
```bash
git push origin main
```

2. **Monitor deployment:**
- Go to GitHub Actions tab
- Watch "Deploy to Cloud Run" workflow
- Verify "Smoke Tests" pass after deployment

### Option 2: Manual Deployment

#### Step 1: Build and Push Backend

```bash
cd backend

# Build image
docker build \
  --platform linux/amd64 \
  -t gcr.io/$GCP_PROJECT_ID/chess-alive-backend:latest \
  .

# Push to GCR
docker push gcr.io/$GCP_PROJECT_ID/chess-alive-backend:latest
```

#### Step 2: Deploy Backend

```bash
# Update cloudrun.yaml with your project ID
sed -i "s/PROJECT_ID/$GCP_PROJECT_ID/g" cloudrun.yaml

# Deploy
gcloud run services replace cloudrun.yaml --region=us-central1

# Get backend URL
BACKEND_URL=$(gcloud run services describe chess-alive-backend \
  --region=us-central1 \
  --format='value(status.url)')

echo "Backend deployed to: $BACKEND_URL"
```

#### Step 3: Build and Push Frontend

```bash
cd ../frontend

# Build with production env vars
docker build \
  --build-arg VITE_API_BASE_URL="${BACKEND_URL}/api/v1" \
  --build-arg VITE_SUPABASE_URL="https://your-project.supabase.co" \
  --build-arg VITE_SUPABASE_PUBLISHABLE_KEY="your-key" \
  --build-arg VITE_POSTHOG_API_KEY="your-key" \
  -t gcr.io/$GCP_PROJECT_ID/chess-alive-frontend:latest \
  .

# Push to GCR
docker push gcr.io/$GCP_PROJECT_ID/chess-alive-frontend:latest
```

#### Step 4: Deploy Frontend

```bash
# Update cloudrun.yaml
sed -i "s/PROJECT_ID/$GCP_PROJECT_ID/g" cloudrun.yaml

# Deploy
gcloud run services replace cloudrun.yaml --region=us-central1

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe chess-alive-frontend \
  --region=us-central1 \
  --format='value(status.url)')

echo "Frontend deployed to: $FRONTEND_URL"
```

#### Step 5: Update CORS Configuration

```bash
# Update backend ALLOWED_ORIGINS with frontend URL
echo "[\"$FRONTEND_URL\"]" | \
  gcloud secrets versions add chess-alive-allowed-origins --data-file=-

# Redeploy backend to pick up new CORS setting
gcloud run services update chess-alive-backend \
  --region=us-central1 \
  --update-env-vars ALLOWED_ORIGINS="[\"$FRONTEND_URL\"]"
```

---

## Post-Deployment

### 1. Run Smoke Tests

```bash
# Backend health
curl https://your-backend-url/health | jq

# Frontend health
curl https://your-frontend-url/health

# Create test game
curl -X POST https://your-backend-url/api/v1/games \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: test-$(uuidgen)" \
  -d '{"game_mode":"pvai","template":"classic"}' | jq
```

### 2. Verify Monitoring

- **Sentry**: Check error tracking dashboard
- **PostHog**: Verify event ingestion
- **Cloud Run**: Monitor metrics (CPU, memory, requests)
- **Cloud Logging**: Check structured logs

### 3. Configure Custom Domain (Optional)

```bash
# Map domain to backend
gcloud run domain-mappings create \
  --service=chess-alive-backend \
  --domain=api.yourdomain.com \
  --region=us-central1

# Map domain to frontend
gcloud run domain-mappings create \
  --service=chess-alive-frontend \
  --domain=yourdomain.com \
  --region=us-central1

# Update DNS records as prompted
```

---

## Monitoring

### Cloud Run Metrics

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=50 \
  --format=json

# Monitor metrics
gcloud run services describe chess-alive-backend \
  --region=us-central1 \
  --format="value(status.traffic)"
```

### Key Metrics to Monitor

- **Response Time**: p95 < 500ms
- **Error Rate**: < 1%
- **Memory Usage**: < 80% of limit
- **CPU Usage**: < 70% average
- **Request Rate**: Track per endpoint

### Alerts to Configure

1. Error rate > 5% for 5 minutes
2. p95 latency > 2 seconds for 5 minutes
3. Memory usage > 90%
4. Health check failures > 3 consecutive

---

## Rollback Procedures

### Automatic Rollback

```bash
# List revisions
gcloud run revisions list \
  --service=chess-alive-backend \
  --region=us-central1

# Rollback to previous revision
PREVIOUS_REVISION=$(gcloud run revisions list \
  --service=chess-alive-backend \
  --region=us-central1 \
  --format="value(name)" \
  --limit=2 | tail -1)

gcloud run services update-traffic chess-alive-backend \
  --to-revisions=$PREVIOUS_REVISION=100 \
  --region=us-central1
```

### Manual Rollback Triggers

- Error rate > 5% for 5 minutes
- p95 latency > 2 seconds for 5 minutes
- Health check failures > 3 consecutive
- Database connection issues
- Critical bug reported

### Rollback Checklist

- [ ] Verify issue in logs/metrics
- [ ] Identify previous stable revision
- [ ] Execute rollback command
- [ ] Verify service health
- [ ] Notify team
- [ ] Document incident

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=50 | grep ERROR

# Common issues:
# - Missing environment variables
# - Secret access permissions
# - Database connection failure
```

### High Memory Usage

```bash
# Check memory metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/memory/utilizations"'

# Solution: Increase memory in cloudrun.yaml
```

### Database Connection Issues

```bash
# Test Supabase connectivity
curl -f https://your-project.supabase.co/rest/v1/

# Check if IP is allowed in Supabase settings
```

### Rate Limit Issues

```bash
# Check Redis connectivity from Cloud Run
# Ensure Redis is in same region
# Verify VPC connector if using Memorystore
```

---

## Maintenance

### Update Dependencies

```bash
# Backend
cd backend
pip list --outdated
pip install -U package-name
pip freeze > requirements.txt

# Frontend
cd frontend
npm outdated
npm update package-name
```

### Database Migrations

```bash
# Apply new Supabase migrations
cd supabase
supabase db push --db-url "postgresql://..."
```

### Scale Configuration

```bash
# Adjust max instances
gcloud run services update chess-alive-backend \
  --max-instances=20 \
  --region=us-central1

# Adjust memory/CPU
gcloud run services update chess-alive-backend \
  --memory=1Gi \
  --cpu=2 \
  --region=us-central1
```

---

## Security Checklist

- [ ] All secrets in Secret Manager (not in code)
- [ ] CORS restricted to frontend domain only
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] HTTPS enforced (automatic with Cloud Run)
- [ ] Service account has minimal permissions
- [ ] Database RLS policies enabled
- [ ] Error messages sanitized
- [ ] Dependency scanning in CI/CD

---

## Performance Optimization

### Cold Start Reduction

- Minimum 1 instance configured
- Startup CPU boost enabled
- Health check configured properly

### Database Optimization

- Connection pooling configured
- Queries indexed properly
- Read replicas for heavy traffic

### Caching Strategy

- Redis for rate limiting
- Browser caching for static assets (1 year)
- API response caching where appropriate

---

## Support Contacts

- **Infrastructure**: DevOps team
- **Backend Issues**: Backend team
- **Frontend Issues**: Frontend team
- **Database**: Supabase support
- **Monitoring**: Sentry/PostHog support

---

## Changelog

Track all production deployments:

| Date | Version | Changes | Deployed By |
|------|---------|---------|-------------|
| YYYY-MM-DD | v1.0.0 | Initial production release | Team |
