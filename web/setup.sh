#!/bin/bash

# RetroBoard Web Interface Setup Script
# This script helps you quickly set up and run the web interface

set -e

echo "🎮 RetroBoard Web Interface Setup"
echo "=================================="
echo ""

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm is not installed"
    echo ""
    echo "Please install pnpm first:"
    echo "  npm install -g pnpm"
    echo ""
    echo "Or use npm/volta/other package managers as documented at:"
    echo "  https://pnpm.io/installation"
    exit 1
fi

echo "✅ pnpm is installed"

# Check if we're in the web directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found"
    echo "Please run this script from the web/ directory"
    exit 1
fi

echo "✅ Found package.json"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "==========="
echo ""
echo "1. Start the RetroBoard server (in the main project directory):"
echo "   python3 server.py"
echo ""
echo "2. Start the web development server (in this directory):"
echo "   pnpm run dev"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:3000"
echo ""
echo "For production builds:"
echo "   pnpm run build"
echo "   pnpm run preview"
echo ""
echo "See README.md for more information."
