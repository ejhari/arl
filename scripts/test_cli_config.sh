#!/bin/bash
# Quick test of CLI configuration

set -e

echo "Testing ARL CLI Configuration"
echo "==============================="
echo ""

# Initialize database
echo "Initializing ARL..."
arl init
echo ""

# Create a test project
echo "Creating test project..."
PROJECT_ID=$(arl project create \
  --name "CLI Config Test" \
  --domain cs \
  --objectives "Test Azure OpenAI configuration" | grep -oP 'Project ID: \K[a-f0-9-]+')

echo "Created project: $PROJECT_ID"
echo ""

# Test hypothesis generation (this will call Azure OpenAI)
echo "Testing hypothesis generation with Azure OpenAI..."
echo "This should use Azure, not Gemini"
echo ""

arl research start \
  --project $PROJECT_ID \
  --request "Test: Compare XGBoost vs Random Forest on wine dataset"

echo ""
echo "==============================="
echo "If you see Azure OpenAI responses above, the configuration is working!"
echo "If you see Gemini errors, the config is still wrong."
echo "==============================="
