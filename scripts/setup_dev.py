#!/usr/bin/env python3
"""
Development setup script for propER.

This script automates the initial setup of the development environment.
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("ℹ️  .env file already exists, skipping creation")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    print("🔄 Creating .env file from template...")
    
    # Read the example file
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Generate a secure secret key
    secret_key = secrets.token_hex(32)
    content = content.replace("your-secret-key-here", secret_key)
    
    # Write the new .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ .env file created with secure secret key")
    return True


def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "logs",
        "app/static/uploads",
        "app/static/exports",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install project dependencies."""
    # Try to install with pip
    result = run_command("pip install -e .[dev]", "Installing development dependencies")
    if result is None:
        # Fallback to requirements.txt
        print("🔄 Falling back to requirements.txt...")
        result = run_command("pip install -r requirements.txt", "Installing dependencies from requirements.txt")
    
    return result is not None


def setup_database():
    """Setup the database."""
    setup_script = Path("scripts/database/setup_database.py")
    if setup_script.exists():
        return run_command("python scripts/database/setup_database.py", "Setting up database") is not None
    else:
        print("⚠️  Database setup script not found, skipping database setup")
        return True


def main():
    """Main setup function."""
    print("🚀 Setting up propER development environment...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Failed to setup database")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Development environment setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your specific configuration")
    print("2. Run 'make run' to start the development server")
    print("3. Visit http://127.0.0.1:5000 in your browser")
    print("\nUseful commands:")
    print("- make help          # Show all available commands")
    print("- make test          # Run tests")
    print("- make format        # Format code")
    print("- make lint          # Run linting")


if __name__ == "__main__":
    main() 