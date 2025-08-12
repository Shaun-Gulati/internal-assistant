#!/bin/bash

echo "🚀 Setting up Internal Assistant Platform with Yarn..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if Yarn is installed, install if not
if ! command -v yarn &> /dev/null; then
    echo "📦 Installing Yarn..."
    npm install -g yarn
fi

echo "✅ Yarn version: $(yarn --version)"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python version: $(python3 --version)"

# Check for existing virtual environment
echo "📦 Setting up Python backend..."
if [ -d ".venv" ]; then
    echo "✅ Found existing virtual environment (.venv)"
    echo "🔧 Activating existing virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No .venv found. Please create a virtual environment first:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   Then run this setup script again."
    exit 1
fi

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    echo "   Trying with --user flag..."
    pip install --user -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Python dependencies even with --user flag"
        exit 1
    fi
fi

echo "✅ Python dependencies installed successfully"
cd ..

# Install frontend dependencies with Yarn
echo "🎨 Setting up Svelte frontend with Yarn..."
cd frontend

# Clean install to avoid conflicts and remove npm lockfile
echo "🧹 Cleaning up old dependencies..."
rm -rf node_modules package-lock.json yarn.lock

echo "📦 Installing dependencies with Yarn..."
yarn install --ignore-engines

# Suppress warnings about deprecated packages
echo "✅ Frontend setup complete!"
echo "⚠️  Some warnings about deprecated packages are normal and safe to ignore."

cd ..

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data embeddings

# Copy environment example
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env file with your API keys"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start the backend: ./start-backend.sh"
echo "3. Start the frontend: ./start-frontend.sh"
echo "4. Or start both: ./start-all.sh"
echo "5. Access the application at http://localhost:3000"
echo ""
echo "Note: The warnings about deprecated packages (rimraf, glob, inflight) are from"
echo "dependencies of dependencies and are safe to ignore in development."
echo ""
echo "For more information, see README.md"
