#!/usr/bin/env python3
"""
SharePoint AI Assistant Setup Script
Helps users set up the Python environment and dependencies.
"""

import sys
import subprocess
import shutil
import os
from pathlib import Path


def check_python_version():
    """Check if Python 3.11+ is available."""
    print("🔍 Checking Python version...")

    # Check current Python version
    current_version = sys.version_info
    if current_version >= (3, 11):
        print(
            f"✅ Current Python version: {current_version.major}.{current_version.minor}.{current_version.micro}"
        )
        return True

    # Check if python3.11 is available
    try:
        result = subprocess.run(
            ["python3.11", "--version"], capture_output=True, text=True, check=True
        )
        print(f"✅ Found Python 3.11: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("❌ Python 3.11+ not found!")
    print("\n📥 Please install Python 3.11 from:")
    print("   • https://www.python.org/downloads/")
    print("   • Ubuntu: sudo apt install python3.11 python3.11-venv")
    print("   • macOS: brew install python@3.11")
    return False


def detect_environment_managers():
    """Detect available environment managers."""
    managers = {}

    # Check for conda
    if shutil.which("conda"):
        managers["conda"] = True
        print("✅ Anaconda/Miniconda detected")

    # Check for uv
    if shutil.which("uv"):
        managers["uv"] = True
        print("✅ UV detected")

    # Python venv is always available if Python is installed
    managers["venv"] = True
    print("✅ Python venv available")

    return managers


def setup_conda_environment():
    """Set up environment using conda."""
    print("\n🐍 Setting up Conda environment...")

    commands = [
        "conda create -n sharepoint-ai python=3.11 -y",
        "conda activate sharepoint-ai",
        "pip install -r requirements/dev.txt",
    ]

    print("Run these commands:")
    for cmd in commands:
        print(f"  {cmd}")

    print("\n💡 After setup, activate with: conda activate sharepoint-ai")


def setup_uv_environment():
    """Set up environment using UV."""
    print("\n⚡ Setting up UV environment...")

    try:
        subprocess.run(["uv", "venv", "--python", "3.11"], check=True)
        print("✅ Virtual environment created with UV")

        # Detect platform for activation command
        if os.name == "nt":  # Windows
            activate_cmd = ".venv\\Scripts\\activate"
        else:  # Unix-like
            activate_cmd = "source .venv/bin/activate"

        print(f"\n💡 Activate with: {activate_cmd}")
        print("💡 Then run: uv pip install -r requirements/dev.txt")

    except subprocess.CalledProcessError as e:
        print(f"❌ UV setup failed: {e}")
        return False

    return True


def setup_venv_environment():
    """Set up environment using standard venv."""
    print("\n🐍 Setting up Python venv environment...")

    # Try python3.11 first, then python
    python_cmd = "python3.11" if shutil.which("python3.11") else "python"

    try:
        subprocess.run([python_cmd, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")

        # Detect platform for activation command
        if os.name == "nt":  # Windows
            activate_cmd = "venv\\Scripts\\activate"
        else:  # Unix-like
            activate_cmd = "source venv/bin/activate"

        print(f"\n💡 Activate with: {activate_cmd}")
        print("💡 Then run: pip install -r requirements/dev.txt")

    except subprocess.CalledProcessError as e:
        print(f"❌ Venv setup failed: {e}")
        return False

    return True


def copy_env_file():
    """Copy .env.example to .env if it doesn't exist."""
    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_example.exists() and not env_file.exists():
        try:
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from .env.example")
            print("💡 Please edit .env with your SharePoint configuration")
        except Exception as e:
            print(f"⚠️ Could not copy .env file: {e}")


def main():
    """Main setup function."""
    print("🚀 SharePoint AI Assistant Setup")
    print("=" * 40)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    print("\n🔍 Detecting environment managers...")
    managers = detect_environment_managers()

    print("\n📋 Choose your setup method:")
    options = []

    if managers.get("conda"):
        options.append(
            (
                "1",
                "Anaconda/Miniconda (Recommended for beginners)",
                setup_conda_environment,
            )
        )

    if managers.get("uv"):
        options.append(("2", "UV (Fast & Modern)", setup_uv_environment))

    options.append(("3", "Python venv (Traditional)", setup_venv_environment))

    for num, desc, _ in options:
        print(f"  {num}. {desc}")

    # Get user choice
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            selected = next((opt for opt in options if opt[0] == choice), None)
            if selected:
                break
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n👋 Setup cancelled.")
            sys.exit(0)

    # Run selected setup
    print(f"\n🛠️ Setting up with {selected[1]}...")
    if selected[2]():
        copy_env_file()

        print("\n🎉 Setup complete!")
        print("\n📝 Next steps:")
        print("  1. Activate your environment (see commands above)")
        print("  2. Install dependencies: pip install -r requirements/dev.txt")
        print("  3. Edit .env with your SharePoint configuration")
        print("  4. Run the application: streamlit run main.py")
        print("\n📖 For detailed instructions, see README.md")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
