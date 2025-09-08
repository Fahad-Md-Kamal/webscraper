#!/usr/bin/env python3
"""
Ollama Setup Script for LangChain Projects
==========================================

This script helps you install Ollama and download LLM models for local use.
It provides an interactive interface to choose from popular models.
"""

import subprocess
import sys
import os
import shutil
from typing import List, Dict, Tuple

# Popular models with their descriptions
AVAILABLE_MODELS = {
    "llama3.2:1b": {
        "name": "Llama 3.2 1B",
        "size": "~1.3GB",
        "description": "Fastest, smallest model. Good for testing and simple tasks.",
        "ram_requirement": "2-4GB RAM"
    },
    "llama3.2:3b": {
        "name": "Llama 3.2 3B", 
        "size": "~2.0GB",
        "description": "Balanced speed and capability. Great for most tasks.",
        "ram_requirement": "4-8GB RAM"
    },
    "llama3.1:8b": {
        "name": "Llama 3.1 8B",
        "size": "~4.7GB", 
        "description": "More capable, good reasoning. Slower but higher quality.",
        "ram_requirement": "8-16GB RAM"
    },
    "deepseek-r1:1.5b": {
        "name": "DeepSeek R1 1.5B",
        "size": "~1.7GB",
        "description": "Fast reasoning model, excellent for logical tasks.",
        "ram_requirement": "2-4GB RAM"
    },
    "deepseek-r1:8b": {
        "name": "DeepSeek R1 8B", 
        "size": "~8.9GB",
        "description": "Advanced reasoning model, great for complex problems.",
        "ram_requirement": "8-16GB RAM"
    },
    "qwen2.5:3b": {
        "name": "Qwen 2.5 3B",
        "size": "~2.0GB",
        "description": "Strong multilingual support, good for international use.",
        "ram_requirement": "4-8GB RAM"
    },
    "phi3.5:3.8b": {
        "name": "Phi 3.5 3.8B",
        "size": "~2.2GB", 
        "description": "Microsoft's efficient model, good performance per size.",
        "ram_requirement": "4-8GB RAM"
    }
}

def print_banner():
    """Print the setup banner."""
    print("=" * 60)
    print("🚀 OLLAMA SETUP FOR LANGCHAIN PROJECTS")
    print("=" * 60)
    print("This script will help you:")
    print("1. Install Ollama (if not already installed)")
    print("2. Choose and download an LLM model")
    print("3. Test the installation")
    print("=" * 60)
    print()

def check_command_exists(command: str) -> bool:
    """Check if a command exists in the system."""
    return shutil.which(command) is not None

def run_command(command: str, check: bool = True) -> Tuple[bool, str]:
    """Run a shell command and return success status and output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            check=check
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def install_ollama() -> bool:
    """Install Ollama using the appropriate method."""
    print("📦 Installing Ollama...")
    
    # Try snap first (most reliable on Ubuntu/Debian)
    if check_command_exists("snap"):
        print("   Using snap package manager...")
        success, output = run_command("sudo snap install ollama", check=False)
        if success:
            print("   ✅ Ollama installed via snap!")
            return True
        else:
            print(f"   ❌ Snap installation failed: {output}")
    
    # Try the official installer
    print("   Using official installer...")
    success, output = run_command("curl -fsSL https://ollama.com/install.sh | sh", check=False)
    if success:
        print("   ✅ Ollama installed via official installer!")
        return True
    else:
        print(f"   ❌ Official installer failed: {output}")
    
    print("   ❌ Failed to install Ollama automatically.")
    print("   Please visit https://ollama.com/download for manual installation.")
    return False

def check_ollama_installation() -> bool:
    """Check if Ollama is properly installed."""
    if not check_command_exists("ollama"):
        return False
    
    # Test if ollama service is accessible
    success, _ = run_command("ollama --version", check=False)
    return success

def start_ollama_service():
    """Start the Ollama service."""
    print("🔄 Starting Ollama service...")
    
    # For snap installation, the service should start automatically
    # For manual installation, we might need to start it
    success, _ = run_command("ollama serve &", check=False)
    
    # Give it a moment to start
    import time
    time.sleep(3)
    
    # Test if service is running
    success, _ = run_command("ollama list", check=False)
    if success:
        print("   ✅ Ollama service is running!")
    else:
        print("   ⚠️  Ollama service may not be running properly.")
        print("   You might need to run 'ollama serve' manually in another terminal.")

def display_model_menu() -> str:
    """Display available models and get user selection."""
    print("🤖 AVAILABLE LLM MODELS")
    print("-" * 50)
    
    models_list = list(AVAILABLE_MODELS.keys())
    
    for i, model_id in enumerate(models_list, 1):
        model_info = AVAILABLE_MODELS[model_id]
        print(f"{i}. {model_info['name']}")
        print(f"   Model ID: {model_id}")
        print(f"   Size: {model_info['size']}")
        print(f"   RAM needed: {model_info['ram_requirement']}")
        print(f"   Description: {model_info['description']}")
        print()
    
    while True:
        try:
            choice = input(f"Select a model (1-{len(models_list)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("Setup cancelled by user.")
                sys.exit(0)
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(models_list):
                selected_model = models_list[choice_num - 1]
                model_info = AVAILABLE_MODELS[selected_model]
                
                print(f"\n📋 You selected: {model_info['name']}")
                print(f"   Model ID: {selected_model}")
                print(f"   Download size: {model_info['size']}")
                print(f"   RAM requirement: {model_info['ram_requirement']}")
                
                confirm = input("\nProceed with this model? (y/n): ").strip().lower()
                if confirm == 'y':
                    return selected_model
                else:
                    print("\nPlease select again:")
                    continue
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")
        except KeyboardInterrupt:
            print("\nSetup cancelled by user.")
            sys.exit(0)

def pull_model(model_id: str) -> bool:
    """Download the specified model."""
    model_info = AVAILABLE_MODELS[model_id]
    print(f"\n⬇️  Downloading {model_info['name']}...")
    print(f"   Size: {model_info['size']} (this may take a while)")
    print("   Press Ctrl+C to cancel if needed")
    
    try:
        success, output = run_command(f"ollama pull {model_id}")
        if success:
            print(f"   ✅ Successfully downloaded {model_info['name']}!")
            return True
        else:
            print(f"   ❌ Failed to download model: {output}")
            return False
    except KeyboardInterrupt:
        print("\n   ⚠️  Download cancelled by user.")
        return False

def test_model(model_id: str) -> bool:
    """Test the installed model."""
    model_info = AVAILABLE_MODELS[model_id]
    print(f"\n🧪 Testing {model_info['name']}...")
    
    test_prompt = "What is the capital of France? Answer in one word."
    
    try:
        success, output = run_command(f'ollama run {model_id} "{test_prompt}"')
        if success and output.strip():
            print(f"   ✅ Model test successful!")
            print(f"   Test response: {output.strip()}")
            return True
        else:
            print(f"   ❌ Model test failed: {output}")
            return False
    except Exception as e:
        print(f"   ❌ Model test failed: {e}")
        return False

def update_course_file(model_id: str):
    """Update the course_one.py file with the selected model."""
    course_file = "course_one.py"
    
    if not os.path.exists(course_file):
        print(f"   ⚠️  {course_file} not found. You'll need to update the model manually.")
        return
    
    try:
        with open(course_file, 'r') as f:
            content = f.read()
        
        # Replace the model in the ChatOllama line
        updated_content = content.replace(
            'ChatOllama(model="llama3.2:3b"',
            f'ChatOllama(model="{model_id}"'
        )
        
        with open(course_file, 'w') as f:
            f.write(updated_content)
        
        print(f"   ✅ Updated {course_file} to use {model_id}")
        
    except Exception as e:
        print(f"   ⚠️  Could not update {course_file}: {e}")
        print(f"   Please manually change the model to: {model_id}")

def main():
    """Main setup function."""
    print_banner()
    
    # Check if Ollama is already installed
    if check_ollama_installation():
        print("✅ Ollama is already installed!")
    else:
        print("📦 Ollama not found. Installing...")
        if not install_ollama():
            print("❌ Setup failed. Please install Ollama manually.")
            sys.exit(1)
    
    # Start Ollama service
    start_ollama_service()
    
    # Show model selection
    selected_model = display_model_menu()
    
    # Pull the selected model
    if not pull_model(selected_model):
        print("❌ Setup failed during model download.")
        sys.exit(1)
    
    # Test the model
    if not test_model(selected_model):
        print("⚠️  Model downloaded but test failed. It might still work.")
    
    # Update course file
    update_course_file(selected_model)
    
    # Final success message
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print(f"✅ Ollama installed and running")
    print(f"✅ Model downloaded: {AVAILABLE_MODELS[selected_model]['name']}")
    print(f"✅ Ready to use model: {selected_model}")
    print()
    print("Next steps:")
    print("1. Run your LangChain code: uv run course_one.py")
    print("2. The model will be used automatically")
    print()
    print("Useful commands:")
    print(f"• Test model: ollama run {selected_model}")
    print("• List models: ollama list")
    print("• Remove model: ollama rm <model_name>")
    print("=" * 60)

if __name__ == "__main__":
    main()
