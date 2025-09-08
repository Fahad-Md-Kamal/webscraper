#!/bin/bash

# Simple bash version of the Ollama setup script
# Usage: ./setup_ollama.sh

set -e

echo "🚀 OLLAMA SETUP SCRIPT"
echo "======================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Ollama if not present
if ! command_exists ollama; then
    echo "📦 Installing Ollama..."
    
    # Try snap first
    if command_exists snap; then
        echo "   Using snap..."
        sudo snap install ollama
    else
        echo "   Using official installer..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    
    echo "✅ Ollama installed!"
else
    echo "✅ Ollama already installed!"
fi

# Start Ollama service
echo "🔄 Starting Ollama service..."
ollama serve &
sleep 3

# Show available models
echo ""
echo "🤖 POPULAR MODELS TO CHOOSE FROM:"
echo "================================="
echo "1. llama3.2:1b     - Fastest, smallest (~1.3GB)"
echo "2. llama3.2:3b     - Balanced speed/quality (~2.0GB) [RECOMMENDED]"
echo "3. llama3.1:8b     - High quality, slower (~4.7GB)"
echo "4. deepseek-r1:1.5b - Fast reasoning (~1.7GB)"
echo "5. deepseek-r1:8b   - Advanced reasoning (~8.9GB)"
echo "6. qwen2.5:3b      - Multilingual support (~2.0GB)"
echo ""

# Get user choice
read -p "Enter model number (1-6) [default: 2]: " choice
case ${choice:-2} in
    1) MODEL="llama3.2:1b" ;;
    2) MODEL="llama3.2:3b" ;;
    3) MODEL="llama3.1:8b" ;;
    4) MODEL="deepseek-r1:1.5b" ;;
    5) MODEL="deepseek-r1:8b" ;;
    6) MODEL="qwen2.5:3b" ;;
    *) echo "Invalid choice, using default: llama3.2:3b"; MODEL="llama3.2:3b" ;;
esac

echo "⬇️  Downloading model: $MODEL"
echo "This may take several minutes depending on your internet speed..."

# Pull the model
if ollama pull "$MODEL"; then
    echo "✅ Model downloaded successfully!"
else
    echo "❌ Failed to download model"
    exit 1
fi

# Test the model
echo "🧪 Testing model..."
if echo "What is 2+2?" | ollama run "$MODEL" > /dev/null; then
    echo "✅ Model test successful!"
else
    echo "⚠️  Model test failed, but it might still work"
fi

# Update course_one.py if it exists
if [ -f "course_one.py" ]; then
    echo "📝 Updating course_one.py with selected model..."
    sed -i "s/llama3.2:3b/$MODEL/g" course_one.py
    echo "✅ Updated course_one.py"
fi

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo "Model ready: $MODEL"
echo ""
echo "Next steps:"
echo "• Run your code: uv run course_one.py"
echo "• Test manually: ollama run $MODEL"
echo ""
echo "Useful commands:"
echo "• List models: ollama list"
echo "• Remove model: ollama rm <model_name>"
