#!/bin/bash

echo "🐍 Starting Internal Assistant Backend..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "📁 Moving to backend directory..."
    cd backend
fi

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "❌ Virtual environment not found (.venv). Please run setup first:"
    echo "   ./setup-yarn.sh"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../.venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Set Python path to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🚀 Starting Flask server..."
echo "🌐 Backend will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python app.py
