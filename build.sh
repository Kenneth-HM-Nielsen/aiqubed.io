#!/bin/bash

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📦 Unzipping vectorstore..."
unzip -o compliance_gpt_backend/vectorstore/compliance-laws.zip -d compliance_gpt_backend/vectorstore/

echo "✅ Build complete."
