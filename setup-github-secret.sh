#!/bin/bash

# Script to help set up GitHub secret for Google Cloud deployment

echo "🔐 Setting up GitHub secret for Google Cloud deployment..."

if [ ! -f "gcp-sa-key.json" ]; then
    echo "❌ Error: gcp-sa-key.json not found!"
    echo "Please run ./setup-gcloud.sh first to create the service account key."
    exit 1
fi

echo ""
echo "📋 GitHub Secret Setup Instructions:"
echo "1. Go to: https://github.com/Dougal-McGuire/api-research/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Name: GCP_SA_KEY"
echo "4. Value: Copy the content below"
echo ""
echo "--- Copy this content ---"
cat gcp-sa-key.json
echo ""
echo "--- End of content ---"
echo ""
echo "5. Click 'Add secret'"
echo ""
echo "🚀 After adding the secret, push your code to trigger deployment!"

# Optionally use GitHub CLI if available
if command -v gh &> /dev/null; then
    echo ""
    echo "🤖 Alternative: Use GitHub CLI to set secret automatically:"
    echo "gh secret set GCP_SA_KEY < gcp-sa-key.json"
fi