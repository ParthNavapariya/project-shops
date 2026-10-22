#!/bin/bash
# =========================================================================
# ReWear AI: One-Click Startup Script
# =========================================================================

echo "======================================================================"
echo "✨ Starting ReWear AI: Pre-Owned Fashion Marketplace & Rental System"
echo "======================================================================"

# Determine directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# 1. Check or activate Virtual Environment
if [ -d "venv" ]; then
    echo "✓ Activating Python virtual environment..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 2. Verify or train Machine Learning Model
if [ ! -f "ml_models/fair_resale_model.joblib" ]; then
    echo "⚙️ Training Scikit-learn Fair Resale Valuation Model..."
    python3 -c "from ml_engine import price_model; price_model.train()"
else
    echo "✓ Machine Learning model is ready."
fi

# 3. Verify Database
echo "✓ Initializing database tables and seed data..."
python3 init_db.py

# 4. Launch Flask Application
echo "======================================================================"
echo "🚀 Application is running on: http://127.0.0.1:5001"
echo "👉 Open your browser to explore the marketplace, rentals, and AI lab!"
echo "======================================================================"

python3 app.py
