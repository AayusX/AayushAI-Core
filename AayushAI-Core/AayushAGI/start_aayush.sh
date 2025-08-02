#!/bin/bash

# AayushAGI Startup Script
# The World's Most Advanced Personal AI Assistant

echo "🤖 Starting AayushAGI - The Ultimate Personal AI Assistant"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "❌ Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if virtual environment should be created
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f ".requirements_installed" ]; then
    echo "📦 Installing required packages..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Mark requirements as installed
    touch .requirements_installed
    echo "✅ All packages installed successfully"
else
    echo "✅ Required packages already installed"
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
    echo "✅ Data directory created"
fi

# Check for audio dependencies (for voice features)
if ! dpkg -l | grep -q portaudio19-dev; then
    echo "⚠️  Audio dependencies not found. Voice features may not work properly."
    echo "   To install: sudo apt-get install portaudio19-dev python3-pyaudio"
fi

# Display system information
echo ""
echo "🖥️  System Information:"
echo "   OS: $(lsb_release -d | cut -f2)"
echo "   Python: $PYTHON_VERSION"
echo "   Working Directory: $(pwd)"
echo "   Memory Available: $(free -h | awk '/^Mem:/ {print $7}')"
echo ""

# Launch AayushAGI
echo "🚀 Launching AayushAGI..."
echo "=================================================="
echo ""

# Run with error handling
python3 main.py

# Handle exit
EXIT_CODE=$?
echo ""
echo "=================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ AayushAGI shutdown completed successfully"
else
    echo "❌ AayushAGI exited with error code: $EXIT_CODE"
fi

# Deactivate virtual environment
deactivate

echo "🤖 Thank you for using AayushAGI!"
echo "   The World's Most Advanced Personal AI Assistant"
