#!/usr/bin/env python3
"""
Cross-platform launcher for the CarMax Store Demo.

This script provides a user-friendly way to launch the demo with automatic
dependency checking and installation guidance.
"""

import os
import sys
import subprocess
import platform
from typing import List, Tuple


def print_banner() -> None:
    """Print a welcome banner."""
    print()
    print("=" * 50)
    print("        🚗 CARMAX STORE DEMO 🚗")
    print("=" * 50)
    print()
    print("Starting CarMax store team simulation...")
    print()


def check_python_version() -> bool:
    """Check if Python version is adequate."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True


def check_dependencies() -> Tuple[bool, List[str]]:
    """Check if required packages are installed."""
    required_packages = ['pygame', 'requests', 'ollama']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    return len(missing_packages) == 0, missing_packages


def install_dependencies(missing_packages: List[str]) -> bool:
    """Attempt to install missing dependencies."""
    print()
    print("📦 Installing missing packages...")
    
    try:
        cmd = [sys.executable, '-m', 'pip', 'install'] + missing_packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        print()
        print("💡 Please install manually:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False


def launch_demo() -> None:
    """Launch the main demo."""
    print()
    print("🎮 Launching CarMax Store Demo...")
    print("   (A pygame window will open with the store interface)")
    print()
    
    try:
        # Import and run the demo
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
        import simple_demo
        simple_demo.main()
    except ImportError as e:
        print(f"❌ Error importing demo: {e}")
        print("   Make sure simple_demo.py is in the app directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        sys.exit(1)


def main() -> None:
    """Main launcher function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        sys.exit(1)
    
    print()
    print("🔍 Checking dependencies...")
    
    # Check dependencies
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        print()
        response = input("📥 Install missing packages automatically? (y/N): ")
        if response.lower() in ['y', 'yes']:
            if not install_dependencies(missing):
                input("Press Enter to exit...")
                sys.exit(1)
        else:
            print()
            print("❌ Cannot run demo without required packages.")
            print("💡 Install them manually with:")
            print(f"   pip install -r app/requirements.txt")
            input("Press Enter to exit...")
            sys.exit(1)
    
    # Launch the demo
    launch_demo()
    
    print()
    print("👋 Thanks for trying the CarMax Store Demo!")
    
    # Wait for user on Windows
    if platform.system() == "Windows":
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()