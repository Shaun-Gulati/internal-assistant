#!/bin/bash

echo "🔍 Checking Internal Assistant Platform Setup..."
echo ""

# Check if we're in the right directory
if [ ! -f "setup-yarn.sh" ]; then
    echo "❌ Please run this script from the internal-assistant directory"
    exit 1
fi

echo "📁 Checking directory structure..."
if [ -d "backend" ] && [ -d "frontend" ] && [ -d "config" ]; then
    echo "✅ Directory structure looks good"
else
    echo "❌ Missing required directories"
    exit 1
fi

echo ""
echo "🐍 Checking Python backend..."

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment exists (.venv)"
    
    # Check if it's properly activated
    source .venv/bin/activate
    
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "✅ Virtual environment can be activated"
        
        # Check if Flask is installed
        if python -c "import flask" 2>/dev/null; then
            echo "✅ Flask is installed"
        else
            echo "❌ Flask is not installed. Run: pip install -r backend/requirements.txt"
        fi
        
        # Check other key packages
        for package in "openai" "requests" "numpy"; do
            if python -c "import $package" 2>/dev/null; then
                echo "✅ $package is installed"
            else
                echo "❌ $package is not installed"
            fi
        done
    else
        echo "❌ Virtual environment activation failed"
    fi
else
    echo "❌ Virtual environment not found (.venv)"
    echo "   Run: ./setup-yarn.sh"
fi

echo ""
echo "🎨 Checking Svelte frontend..."

# Check if node_modules exists
if [ -d "frontend/node_modules" ]; then
    echo "✅ Node modules installed"
    
    # Check if key packages are installed
    cd frontend
    if [ -d "node_modules/svelte" ]; then
        echo "✅ Svelte is installed"
    else
        echo "❌ Svelte is not installed"
    fi
    
    if [ -d "node_modules/vite" ]; then
        echo "✅ Vite is installed"
    else
        echo "❌ Vite is not installed"
    fi
    
    if [ -d "node_modules/lucide-svelte" ]; then
        echo "✅ Lucide Svelte is installed"
    else
        echo "❌ Lucide Svelte is not installed"
    fi
    cd ..
else
    echo "❌ Node modules not found"
    echo "   Run: ./setup-yarn.sh"
fi

echo ""
echo "⚙️ Checking configuration..."

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ Environment file exists"
else
    echo "❌ Environment file not found"
    echo "   Run: ./setup-yarn.sh"
fi

# Check if data directories exist (these are created when app runs)
if [ -d "data" ] && [ -d "embeddings" ]; then
    echo "✅ Data directories exist"
else
    echo "ℹ️  Data directories not found (will be created when app starts)"
fi

echo ""
echo "🎯 Setup Status Summary:"
echo "If you see any ❌ items above, run: ./setup-yarn.sh"
echo "If everything shows ✅ or ℹ️, you're ready to start the application!"
echo ""
echo "To start the application:"
echo "  ./start-all.sh"
