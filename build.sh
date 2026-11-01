#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "===> Upgrading pip and installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "===> Building React Vite Frontend..."
cd frontend
npm install
npm run build
cd ..

echo "===> Build complete! Frontend static assets ready in frontend/dist."
