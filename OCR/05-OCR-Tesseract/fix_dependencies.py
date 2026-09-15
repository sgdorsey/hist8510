#!/usr/bin/env python3
"""
Fix Dependencies Script
======================

This script helps resolve common dependency issues with the OCR demo,
particularly the numpy/pandas compatibility issue.

Usage:
    python fix_dependencies.py
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and show the result."""
    print(f"\n{description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
        else:
            print("❌ Failed!")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function to fix dependencies."""
    print("=" * 60)
    print("DEPENDENCY FIX SCRIPT")
    print("=" * 60)
    
    print("This script will help resolve common dependency issues.")
    print("The main issue is usually numpy/pandas compatibility.")
    
    # Commands to try in order
    fix_commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install --upgrade numpy", "Upgrading numpy"),
        ("pip install --upgrade pandas", "Upgrading pandas"),
        ("pip install --upgrade pytesseract", "Upgrading pytesseract"),
        ("pip install --force-reinstall pytesseract", "Force reinstalling pytesseract"),
    ]
    
    print("\nAttempting to fix dependencies...")
    
    for command, description in fix_commands:
        success = run_command(command, description)
        if not success:
            print(f"⚠️  {description} failed, continuing...")
    
    print("\n" + "=" * 60)
    print("ALTERNATIVE SOLUTIONS")
    print("=" * 60)
    
    print("""
If the above didn't work, try these alternatives:

1. CREATE A NEW VIRTUAL ENVIRONMENT:
   python3 -m venv ocr_env        # macOS has no bare `python` command
   source ocr_env/bin/activate    # On Windows: ocr_env\\Scripts\\activate
   pip install -r requirements.txt

2. USE CONDA INSTEAD OF PIP:
   conda install numpy pandas pytesseract
   conda install -c conda-forge opencv matplotlib pillow pdf2image

3. DO NOT PIN OLD VERSIONS ON A NEW PYTHON:
   On Python 3.13+ there are no prebuilt wheels for numpy 1.x or pandas 2.x,
   so pip tries to compile them from source and fails. Let pip pick the
   newest version instead of pinning, e.g.:
   pip install --upgrade numpy pandas pytesseract

4. SKIP THE OCR DEMO FOR NOW:
   You can still run PDF conversion and preprocessing:
   python pdf_to_images_demo.py
   python 01_noise_reduction_demo.py

5. INSTALL THE SYSTEM TOOLS:
   pip cannot install these -- they are separate programs:
   brew install tesseract poppler
""")
    
    print("\n" + "=" * 60)
    print("TESTING OCR DEMO")
    print("=" * 60)
    
    # Test if OCR demo works now
    test_command = "python ocr_demo.py --check-deps"
    print("Testing OCR demo...")
    
    try:
        result = subprocess.run([sys.executable, "ocr_demo.py", "--check-deps"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ OCR demo dependencies are working!")
            print("You can now run: python ocr_demo.py")
        else:
            print("❌ OCR demo still has issues")
            print("Try the alternative solutions above")
    except Exception as e:
        print(f"❌ Error testing OCR demo: {str(e)}")

if __name__ == "__main__":
    main()
