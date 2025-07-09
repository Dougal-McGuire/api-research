#!/bin/bash

set -e

echo "🚀 Setting up Google Cloud for api-research deployment..."

# Generate unique project ID
PROJECT_ID="api-research-$(date +%Y%m%d%H%M)"
SERVICE_NAME="api-research"
REGION="europe-west1"

echo "📝 Project ID: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "⚙️  Service: $SERVICE_NAME"

# Authenticate to Google Cloud
echo "🔐 Authenticating to Google Cloud..."
gcloud auth login

# Create project
echo "🏗️  Creating Google Cloud project..."
gcloud projects create "$PROJECT_ID" --name="API Research" --set-as-default

# Set current project
gcloud config set project "$PROJECT_ID"

# Enable billing (user needs to link billing account)
echo "💳 Please enable billing for this project in the Google Cloud Console:"
echo "    https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
echo ""
read -p "Press Enter when billing is enabled..."

# Enable required APIs
echo "🔌 Enabling required Google Cloud APIs..."
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  cloudresourcemanager.googleapis.com

# Create Artifact Registry repository
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create "$SERVICE_NAME" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Docker repository for API Research"

# Create service account for deployment
echo "👤 Creating service account..."
SA_NAME="$SERVICE_NAME-deploy"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts create "$SA_NAME" \
  --display-name="API Research Deploy Service Account" \
  --description="Service account for automated deployment"

# Grant necessary permissions
echo "🔑 Granting permissions to service account..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.invoker"

# Create and download service account key
echo "🗝️  Creating service account key..."
gcloud iam service-accounts keys create "gcp-sa-key.json" \
  --iam-account="$SA_EMAIL"

# Update GitHub Actions workflow with correct project ID
echo "📝 Updating GitHub Actions workflow..."
sed -i "s/PROJECT_ID: api-research/PROJECT_ID: $PROJECT_ID/" .github/workflows/deploy.yml

echo ""
echo "✅ Google Cloud setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add the service account key to GitHub Secrets:"
echo "   - Go to: https://github.com/Dougal-McGuire/api-research/settings/secrets/actions"
echo "   - Add secret: GCP_SA_KEY"
echo "   - Value: Copy the contents of gcp-sa-key.json"
echo ""
echo "2. The service account key is in: gcp-sa-key.json"
echo "3. Project ID: $PROJECT_ID"
echo "4. Service Account: $SA_EMAIL"
echo ""
echo "🚀 After adding the secret, push your code to trigger deployment!"

# Clean up key file for security
echo "🧹 Cleaning up key file..."
rm -f gcp-sa-key.json

echo "✅ Setup complete! Ready for deployment."