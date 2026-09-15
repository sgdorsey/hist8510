#!/usr/bin/env python3
"""
Virtual Environment Setup Script
===============================

This script helps you set up a virtual environment for the OCR project
to avoid dependency conflicts.

Usage:
    python3 setup_venv.py
"""

import subprocess
import shutil
import sys
import os
from pathlib import Path

# Always build the venv with the interpreter that is running this script.
# On macOS there is no bare `python` command, only `python3`.
PYTHON = sys.executable

def run_command(command, description, check=True):
    """Run a command and show the result."""
    print(f"\n{description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout and len(result.stdout.strip()) < 200:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print("❌ Failed!")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_system_tools():
    """Check for the non-Python programs the demos shell out to.

    These cannot be installed by pip:
      - tesseract: the OCR engine itself (pytesseract is only a wrapper)
      - pdftoppm:  part of poppler, used by pdf2image to rasterize PDFs
    """
    tools = {
        'tesseract': ('Tesseract OCR', 'brew install tesseract',
                      'sudo apt-get install tesseract-ocr',
                      'https://github.com/UB-Mannheim/tesseract/wiki'),
        'pdftoppm': ('Poppler (for PDF conversion)', 'brew install poppler',
                     'sudo apt-get install poppler-utils',
                     'https://github.com/oschwartz10612/poppler-windows/releases'),
    }

    missing = []
    for command, (label, mac, linux, windows) in tools.items():
        if shutil.which(command):
            print(f"✅ {label} found")
        else:
            print(f"⚠️  {label} NOT found")
            missing.append((label, mac, linux, windows))

    if missing:
        print("\nThese are system programs, so pip cannot install them.")
        print("Install them before running the demos:\n")
        for label, mac, linux, windows in missing:
            print(f"  {label}")
            print(f"    macOS:   {mac}")
            print(f"    Linux:   {linux}")
            print(f"    Windows: {windows}")
        print()

    # Not fatal: the venv is still worth creating.
    return len(missing) == 0


def create_virtual_environment():
    """Create virtual environment."""
    venv_name = "ocr_env"
    
    # Check if virtual environment already exists
    if Path(venv_name).exists():
        print(f"⚠️  Virtual environment '{venv_name}' already exists")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response == 'y':
            print("Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_name)
        else:
            print("Using existing virtual environment")
            return True
    
    # Create virtual environment
    return run_command(f'"{PYTHON}" -m venv {venv_name}', "Creating virtual environment")

def install_dependencies():
    """Install dependencies in virtual environment."""
    venv_name = "ocr_env"
    
    # Determine activation command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = f"{venv_name}\\Scripts\\activate"
        pip_cmd = f"{venv_name}\\Scripts\\pip"
    else:  # macOS/Linux
        activate_cmd = f"source {venv_name}/bin/activate"
        pip_cmd = f"{venv_name}/bin/pip"
    
    # Install dependencies
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -r requirements.txt", "Installing project dependencies"),
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success

def test_installation():
    """Test if the installation works."""
    venv_name = "ocr_env"
    
    # Determine python command based on OS
    if os.name == 'nt':  # Windows
        python_cmd = f"{venv_name}\\Scripts\\python"
    else:  # macOS/Linux
        python_cmd = f"{venv_name}/bin/python"
    
    # Test OCR demo
    return run_command(f"{python_cmd} ocr_demo.py --check-deps", "Testing OCR demo")

def main():
    """Main setup function."""
    print("=" * 60)
    print("VIRTUAL ENVIRONMENT SETUP")
    print("=" * 60)
    
    print("This script will:")
    print("1. Create a virtual environment called 'ocr_env'")
    print("2. Install all required dependencies")
    print("3. Test that everything works")

    # Check Python version
    if not check_python_version():
        return 1

    # Check for system tools (tesseract, poppler) -- warns but does not stop
    system_tools_ok = check_system_tools()

    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return 1
    
    # Test installation
    if not test_installation():
        print("⚠️  Installation completed but testing failed")
        if not system_tools_ok:
            print("This is expected until you install the system tools listed above.")

    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)

    print("""
To use your virtual environment:

1. ACTIVATE the environment:
   macOS/Linux: source ocr_env/bin/activate
   Windows:     ocr_env\\Scripts\\activate

2. RUN your demos (in order):
   python pdf_to_images_demo.py          # PDF -> images
   python 01_noise_reduction_demo.py     # preprocessing
   python 02_contrast_enhancement_demo.py
   python 03_thresholding_demo.py
   python ocr_demo.py                    # run OCR

3. DEACTIVATE when done:
   deactivate

Your virtual environment is isolated from your system Python,
so you won't have dependency conflicts!
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
