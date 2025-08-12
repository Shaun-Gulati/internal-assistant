#!/bin/bash

echo "🚀 Starting Internal Assistant Frontend..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "📁 Moving to frontend directory..."
    cd frontend
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    yarn install --ignore-engines
fi

echo "🎨 Starting development server..."
echo "🌐 Frontend will be available at: http://localhost:3000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

yarn dev
