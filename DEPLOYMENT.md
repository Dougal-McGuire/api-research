# Deployment Guide

This guide explains how to deploy the api-research project to Google Cloud Run with automated CI/CD.

## Overview

The project uses:
- **GitHub Actions** for CI/CD pipeline
- **Google Cloud Run** for container hosting
- **Google Artifact Registry** for Docker image storage
- **Automated deployment** on every push to main branch

## Quick Setup

### 1. Prerequisites
- Google Cloud account with billing enabled
- GitHub repository (already created)
- Google Cloud SDK installed locally

### 2. Run Setup Script
```bash
./setup-gcloud.sh
```

This script will:
- Create Google Cloud project
- Enable required APIs
- Set up Artifact Registry
- Create service account with proper permissions
- Generate service account key

### 3. Add GitHub Secret
After running the setup script, add the service account key to GitHub:

**Method 1: Manual**
1. Go to: https://github.com/Dougal-McGuire/api-research/settings/secrets/actions
2. Click "New repository secret"
3. Name: `GCP_SA_KEY`
4. Value: Contents of the generated `gcp-sa-key.json` file

**Method 2: Using GitHub CLI**
```bash
gh secret set GCP_SA_KEY < gcp-sa-key.json
```

### 4. Deploy
Push to main branch to trigger deployment:
```bash
git push origin main
```

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Google Cloud Project
```bash
PROJECT_ID="api-research-$(date +%Y%m%d%H%M)"
gcloud projects create "$PROJECT_ID" --name="API Research"
gcloud config set project "$PROJECT_ID"
```

### 2. Enable APIs
```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com
```

### 3. Create Artifact Registry
```bash
gcloud artifacts repositories create api-research \
  --repository-format=docker \
  --location=europe-west1
```

### 4. Create Service Account
```bash
gcloud iam service-accounts create api-research-deploy \
  --display-name="API Research Deploy"

# Grant permissions
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:api-research-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:api-research-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:api-research-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### 5. Create Service Account Key
```bash
gcloud iam service-accounts keys create gcp-sa-key.json \
  --iam-account="api-research-deploy@$PROJECT_ID.iam.gserviceaccount.com"
```

### 6. Update GitHub Actions
Update `.github/workflows/deploy.yml` with your project ID:
```yaml
env:
  PROJECT_ID: your-project-id-here  # Replace with actual project ID
```

## Deployment Pipeline

The GitHub Actions workflow:

1. **Checkout** - Gets the latest code
2. **Setup Node.js** - Installs Node.js 20 with npm caching
3. **Install Dependencies** - Runs `npm install` in frontend directory
4. **Build Frontend** - Runs `npm run build` to create production build
5. **Authenticate** - Authenticates with Google Cloud using service account
6. **Build Docker Image** - Builds production Docker image
7. **Push to Registry** - Pushes image to Google Artifact Registry
8. **Deploy to Cloud Run** - Deploys to Google Cloud Run
9. **Show URL** - Displays the deployed service URL

## Configuration

### Environment Variables
The deployment uses these environment variables (configured in GitHub Actions):
- `PROJECT_ID`: Google Cloud project ID
- `SERVICE_NAME`: Cloud Run service name (api-research)
- `REGION`: Deployment region (europe-west1)

### Cloud Run Configuration
- **Memory**: 1GB
- **CPU**: 1 vCPU
- **Port**: 8000
- **Max Instances**: 10
- **Min Instances**: 0 (scales to zero)
- **Concurrency**: 80 requests per instance
- **Timeout**: 300 seconds

## Monitoring Deployment

### Check Deployment Status
1. Go to GitHub Actions: https://github.com/Dougal-McGuire/api-research/actions
2. Click on the latest workflow run
3. Monitor each step's progress

### View Deployed Service
1. Go to Google Cloud Console: https://console.cloud.google.com/run
2. Select your project
3. Click on the `api-research` service
4. View service URL and logs

### Access Deployed Application
After successful deployment, your application will be available at:
- **Frontend**: `https://your-service-url.run.app`
- **API**: `https://your-service-url.run.app/api`
- **API Docs**: `https://your-service-url.run.app/docs`

## Troubleshooting

### Common Issues

**1. Authentication Failed**
- Ensure `GCP_SA_KEY` secret is correctly set in GitHub
- Verify service account has necessary permissions

**2. Build Failed**
- Check if all dependencies are properly listed in package.json
- Ensure frontend builds successfully locally

**3. Deployment Failed**
- Verify Google Cloud project has billing enabled
- Check if required APIs are enabled
- Ensure Docker image builds successfully

**4. Service Not Accessible**
- Check if Cloud Run service allows unauthenticated access
- Verify the service is deployed in the correct region

### Debug Commands
```bash
# Check project configuration
gcloud config list

# View Cloud Run services
gcloud run services list

# Check service logs
gcloud run services logs read api-research --region=europe-west1

# Test local Docker build
docker build -t test-build .
docker run -p 8000:8000 test-build
```

## Cost Optimization

### Development
- Use the included development environment (free)
- Only deploy to production when ready

### Production
- Cloud Run scales to zero when not in use
- Pay only for actual usage
- Monitor usage in Google Cloud Console

## Security

### Best Practices
- Service account has minimal required permissions
- GitHub secrets are encrypted
- Docker image is scanned for vulnerabilities
- HTTPS is enforced by Cloud Run

### Regular Maintenance
- Rotate service account keys periodically
- Update dependencies regularly
- Monitor security alerts

## Support

For issues:
1. Check GitHub Actions logs
2. Review Google Cloud Console logs
3. Verify configuration matches this guide
4. Check Google Cloud Run documentation