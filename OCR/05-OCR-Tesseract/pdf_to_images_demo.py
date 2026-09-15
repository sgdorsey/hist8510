#!/usr/bin/env python3
"""
PDF to Images Demo
=================

This demo script converts PDF files to individual images for OCR preprocessing.
It demonstrates how to:
- Extract pages from PDF files
- Convert to grayscale for better OCR processing (optional)
- Save images with proper naming conventions
- Handle different PDF formats and quality settings
- Choose between color and grayscale output

Usage:
    python pdf_to_images_demo.py

The script will:
1. Look for PDFs in the pdf/ directory
2. Let you choose quality settings (high/medium/low)
3. Let you choose grayscale conversion (recommended for OCR)
4. Convert each page to a high-quality image
5. Save images in processed-imgs/ directory
"""

import os
import sys
from pathlib import Path
import argparse

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = {
        'pdf2image': 'pdf2image',
        'PIL': 'Pillow',
        'cv2': 'opencv-python'
    }
    
    missing_packages = []
    
    for package, install_name in required_packages.items():
        try:
            if package == 'pdf2image':
                import pdf2image
            elif package == 'PIL':
                from PIL import Image
            elif package == 'cv2':
                import cv2
        except ImportError:
            missing_packages.append(install_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("\nNote: pdf2image also requires poppler-utils:")
        print("   macOS: brew install poppler")
        print("   Ubuntu: sudo apt-get install poppler-utils")
        print("   Windows: Download from https://github.com/oschwartz10612/poppler-windows")
        return False
    
    print("✅ All required packages are installed")
    return True

def convert_pdf_to_images(pdf_path, output_dir, dpi=300, quality='high', grayscale=True):
    """
    Convert PDF pages to individual images with optional grayscale conversion.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save images
        dpi: Resolution for image conversion (higher = better quality, larger files)
        quality: 'high', 'medium', or 'low' quality setting
        grayscale: Convert images to grayscale for better OCR processing
    """
    try:
        from pdf2image import convert_from_path
        from PIL import Image
        import cv2
        
        print(f"Converting PDF: {pdf_path.name}")
        
        # Quality settings
        quality_settings = {
            'high': {'dpi': 300, 'format': 'PNG'},
            'medium': {'dpi': 200, 'format': 'PNG'},
            'low': {'dpi': 150, 'format': 'JPEG'}
        }
        
        settings = quality_settings.get(quality, quality_settings['high'])
        actual_dpi = dpi if dpi else settings['dpi']
        
        print(f"  Quality: {quality} (DPI: {actual_dpi})")
        print(f"  Grayscale conversion: {'Yes' if grayscale else 'No'}")
        
        # Convert PDF to images
        images = convert_from_path(
            pdf_path,
            dpi=actual_dpi,
            fmt=settings['format'].lower(),
            thread_count=2  # Use 2 threads for faster processing
        )
        
        print(f"  Extracted {len(images)} pages")
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(exist_ok=True)
        
        # Process each page
        saved_images = []
        base_name = pdf_path.stem  # Get filename without extension
        
        for i, image in enumerate(images, 1):
            # Process image based on grayscale setting
            if grayscale:
                # Convert to grayscale for OCR optimization
                if image.mode != 'L':
                    processed_image = image.convert('L')
                    print(f"    Page {i}: Converted to grayscale")
                else:
                    processed_image = image
                    print(f"    Page {i}: Already grayscale")
            else:
                # Keep original color mode
                processed_image = image
                print(f"    Page {i}: Keeping original color mode ({image.mode})")
            
            # Generate filename
            if len(images) == 1:
                filename = f"{base_name}.png"
            else:
                filename = f"{base_name}_page_{i:03d}.png"
            
            output_path = output_dir / filename
            
            # Save as PNG for lossless quality
            processed_image.save(output_path, 'PNG', optimize=True)
            saved_images.append(output_path)
            
            print(f"    Saved: {filename} ({processed_image.size[0]}x{processed_image.size[1]})")
        
        return saved_images
        
    except Exception as e:
        print(f"❌ Error converting {pdf_path.name}: {str(e)}")
        return []

def demonstrate_pdf_conversion():
    """Demonstrate PDF to images conversion."""
    print("=" * 60)
    print("PDF TO IMAGES CONVERSION DEMO")
    print("=" * 60)
    
    # Set up directories
    pdf_dir = Path(__file__).parent / "pdf"
    output_dir = Path(__file__).parent / "processed-imgs"
    
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        print("Please create the pdf/ directory and add PDF files to convert.")
        return
    
    # Find PDF files
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in: {pdf_dir}")
        print("Please add PDF files to the pdf/ directory.")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s):")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    print(f"\nOutput directory: {output_dir}")
    
    # Ask user for quality preference
    print("\nQuality Options:")
    print("  1. High (300 DPI) - Best quality, larger files")
    print("  2. Medium (200 DPI) - Good quality, moderate file size")
    print("  3. Low (150 DPI) - Lower quality, smaller files")
    
    while True:
        try:
            choice = input("\nChoose quality (1-3): ").strip()
            if choice.lower() in ['q', 'quit', 'exit']:
                print("Demo cancelled.")
                return
            
            choice_num = int(choice)
            if choice_num == 1:
                quality = 'high'
                break
            elif choice_num == 2:
                quality = 'medium'
                break
            elif choice_num == 3:
                quality = 'low'
                break
            else:
                print("Please enter 1, 2, or 3")
        except ValueError:
            print("Please enter a valid number")
    
    # Ask user for grayscale preference
    print("\nGrayscale Conversion:")
    print("  1. Yes - Convert to grayscale (recommended for OCR)")
    print("  2. No - Keep original color")
    
    while True:
        try:
            gray_choice = input("\nConvert to grayscale? (1-2): ").strip()
            if gray_choice.lower() in ['q', 'quit', 'exit']:
                print("Demo cancelled.")
                return
            
            gray_num = int(gray_choice)
            if gray_num == 1:
                grayscale = True
                break
            elif gray_num == 2:
                grayscale = False
                break
            else:
                print("Please enter 1 or 2")
        except ValueError:
            print("Please enter a valid number")
    
    print(f"\nSelected quality: {quality}")
    print(f"Grayscale conversion: {'Yes' if grayscale else 'No'}")
    print("-" * 50)
    
    # Convert each PDF
    total_images = 0
    successful_pdfs = 0
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        saved_images = convert_pdf_to_images(pdf_file, output_dir, quality=quality, grayscale=grayscale)
        
        if saved_images:
            total_images += len(saved_images)
            successful_pdfs += 1
            print(f"✅ Successfully converted {len(saved_images)} pages")
        else:
            print(f"❌ Failed to convert {pdf_file.name}")
    
    # Summary
    print("\n" + "=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    print(f"PDFs processed: {successful_pdfs}/{len(pdf_files)}")
    print(f"Total images created: {total_images}")
    print(f"Output directory: {output_dir}")
    
    if total_images > 0:
        print(f"\n✅ Images saved successfully!")
        print("You can now use these images with the preprocessing demos:")
        print("  python 01_noise_reduction_demo.py")
        print("  python 02_contrast_enhancement_demo.py")
        print("  python 03_thresholding_demo.py")
    else:
        print("\n❌ No images were created. Check the error messages above.")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Convert PDF files to images for OCR preprocessing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_to_images_demo.py                    # Interactive mode
  python pdf_to_images_demo.py --quality high     # High quality conversion
  python pdf_to_images_demo.py --quality low      # Low quality conversion
        """
    )
    
    parser.add_argument('--quality', choices=['high', 'medium', 'low'], 
                       default=None, help='Quality setting for conversion')
    parser.add_argument('--check-deps', action='store_true',
                       help='Check if required dependencies are installed')
    
    args = parser.parse_args()
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    if args.check_deps:
        return 0
    
    # Run the demo
    demonstrate_pdf_conversion()
    
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
