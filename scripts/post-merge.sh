#!/bin/bash
set -e

# Post-merge setup script for EJTech CRM
# Runs automatically after each task agent merge.
# Must be idempotent and non-interactive.

echo "==> Installing Python dependencies..."
pip install --quiet -r requirements.txt

echo "==> Post-merge setup complete."
