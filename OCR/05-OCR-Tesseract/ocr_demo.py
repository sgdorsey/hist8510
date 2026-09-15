#!/usr/bin/env python3
"""
Simple OCR Demo for Historical Documents
=======================================

This simplified demo script demonstrates how to use Tesseract OCR on 
preprocessed images using PSM 3 (fully automatic page segmentation).

Key features:
- Simple OCR with PSM 3 (default mode)
- Text cleaning and formatting
- Basic confidence scoring
- Results saved to text files

Usage:
    python ocr_demo.py
"""

import os
import sys
import re
from pathlib import Path
import argparse

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = {
        'PIL': 'Pillow',
        'cv2': 'opencv-python'
    }
    
    missing_packages = []
    
    for package, install_name in required_packages.items():
        try:
            if package == 'PIL':
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
        return False
    
    # Check if Tesseract is installed (try to avoid pandas import issue)
    try:
        # Try to import pytesseract without triggering pandas
        import subprocess
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ All required packages are installed")
            print(f"✅ Tesseract OCR found: {result.stdout.split()[1]}")
            return True
        else:
            print("❌ Tesseract OCR not found")
            print("Please install Tesseract OCR:")
            print("   macOS: brew install tesseract")
            print("   Ubuntu: sudo apt-get install tesseract-ocr")
            print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print("❌ Tesseract OCR not found")
        print("Please install Tesseract OCR:")
        print("   macOS: brew install tesseract")
        print("   Ubuntu: sudo apt-get install tesseract-ocr")
        print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def get_available_images():
    """Get list of available images for OCR."""
    processed_dir = Path(__file__).parent / "processed-imgs"
    images_dir = Path(__file__).parent / "images"
    
    # Get images from both directories
    processed_images = []
    original_images = []
    
    if processed_dir.exists():
        processed_images = list(processed_dir.glob("*.png")) + list(processed_dir.glob("*.jpg"))
    
    if images_dir.exists():
        original_images = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
    
    return processed_images, original_images

def explain_psm3():
    """Explain PSM 3 mode."""
    print("\n" + "=" * 60)
    print("PSM 3 - FULLY AUTOMATIC PAGE SEGMENTATION")
    print("=" * 60)
    
    print("PSM 3 is Tesseract's default mode and works well for most documents.")
    print("It automatically:")
    print("- Detects text blocks and paragraphs")
    print("- Handles multiple columns")
    print("- Processes text in reading order")
    print("- Works well with historical documents")
    print("\nThis mode is recommended for most OCR tasks.")

def run_ocr_psm3(image_path, language='eng'):
    """Run OCR with PSM 3 mode."""
    try:
        # Import pytesseract only when needed
        import pytesseract
        from PIL import Image
        
        # Load image
        image = Image.open(image_path)
        
        # Configure Tesseract with PSM 3
        config = f'--psm 3 -l {language}'
        
        # Run OCR
        text = pytesseract.image_to_string(image, config=config)
        
        # Get confidence data (simplified to avoid pandas issues)
        try:
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
        except Exception:
            # If data extraction fails, just return basic info
            data = {'conf': []}
        
        return text, data
        
    except ImportError as e:
        print(f"❌ pytesseract import error: {str(e)}")
        print("This might be due to numpy/pandas compatibility issues.")
        print("Try: pip install --upgrade numpy pandas pytesseract")
        return None, None
    except Exception as e:
        print(f"❌ Error running OCR: {str(e)}")
        return None, None

def analyze_text_confidence(data):
    """Analyze OCR confidence scores."""
    if not data or 'conf' not in data:
        return None
    
    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
    
    if not confidences:
        return None
    
    return {
        'mean': sum(confidences) / len(confidences),
        'min': min(confidences),
        'max': max(confidences),
        'count': len(confidences)
    }

def clean_text(text):
    """Clean and format OCR text."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Fix common OCR errors
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)  # Add space after punctuation
    
    return text


def demonstrate_ocr(image_path):
    """Demonstrate OCR with PSM 3."""
    print("=" * 60)
    print("OCR DEMONSTRATION - PSM 3")
    print("=" * 60)
    
    print(f"Processing: {Path(image_path).name}")
    print("-" * 50)
    
    # Run OCR with PSM 3
    print("Running OCR with PSM 3...")
    text, data = run_ocr_psm3(image_path)
    
    if text and data:
        # Analyze confidence
        confidence = analyze_text_confidence(data)
        
        # Clean text
        cleaned_text = clean_text(text)
        
        # Count words
        word_count = len(cleaned_text.split()) if cleaned_text else 0
        
        result = {
            'text': cleaned_text,
            'confidence': confidence,
            'word_count': word_count
        }
        
        print(f"Words extracted: {word_count}")
        if confidence:
            print(f"Confidence: {confidence['mean']:.1f}% (min: {confidence['min']}, max: {confidence['max']})")
        
        # Show first 200 characters
        preview = cleaned_text[:200] + "..." if len(cleaned_text) > 200 else cleaned_text
        print(f"\nText Preview:")
        print("-" * 50)
        print(preview)
        
        return {3: result}  # Return in same format as before for compatibility
    else:
        print("❌ Failed to extract text")
        return {}

def process_all_images(image_list, output_dir):
    """Process all images in a list and save results."""
    print("=" * 60)
    print("BATCH OCR PROCESSING - PSM 3")
    print("=" * 60)
    
    print(f"Processing {len(image_list)} image(s)...")
    print("-" * 50)
    
    total_words = 0
    successful_images = 0
    
    for i, image_path in enumerate(image_list, 1):
        print(f"\n[{i}/{len(image_list)}] Processing: {Path(image_path).name}")
        
        # Run OCR
        text, data = run_ocr_psm3(image_path)
        
        if text and data:
            # Analyze confidence
            confidence = analyze_text_confidence(data)
            
            # Clean text
            cleaned_text = clean_text(text)
            
            # Count words
            word_count = len(cleaned_text.split()) if cleaned_text else 0
            total_words += word_count
            
            # Save individual result
            base_name = Path(image_path).stem
            output_file = output_dir / f"{base_name}_psm_3.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"OCR Results - PSM 3\n")
                f.write(f"Image: {Path(image_path).name}\n")
                f.write(f"Word count: {word_count}\n")
                if confidence:
                    f.write(f"Confidence: {confidence['mean']:.1f}%\n")
                f.write("-" * 50 + "\n\n")
                f.write(cleaned_text)
            
            print(f"  ✅ Words: {word_count}, Confidence: {confidence['mean']:.1f}%" if confidence else f"  ✅ Words: {word_count}")
            successful_images += 1
        else:
            print(f"  ❌ Failed to extract text")
    
    print(f"\n{'='*50}")
    print("BATCH PROCESSING SUMMARY")
    print("=" * 50)
    print(f"Images processed: {successful_images}/{len(image_list)}")
    print(f"Total words extracted: {total_words}")
    print(f"Average words per image: {total_words/successful_images:.1f}" if successful_images > 0 else "No successful extractions")

def save_ocr_results(results, image_path, output_dir):
    """Save OCR results to file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    base_name = Path(image_path).stem
    
    # Save PSM 3 results
    if 3 in results and results[3]['text']:
        data = results[3]
        output_file = output_dir / f"{base_name}_psm_3.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"OCR Results - PSM 3\n")
            f.write(f"Image: {Path(image_path).name}\n")
            f.write(f"Word count: {data['word_count']}\n")
            if data['confidence']:
                f.write(f"Confidence: {data['confidence']['mean']:.1f}%\n")
            f.write("-" * 50 + "\n\n")
            f.write(data['text'])
        
        print(f"✅ Saved PSM 3 results to: {output_file.name}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Simple OCR demo for historical documents using PSM 3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ocr_demo.py                    # Interactive mode
  python ocr_demo.py --check-deps      # Check dependencies
        """
    )
    
    parser.add_argument('--check-deps', action='store_true',
                       help='Check if required dependencies are installed')
    
    args = parser.parse_args()
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    if args.check_deps:
        return 0
    
    # Get available images
    processed_images, original_images = get_available_images()
    
    if not processed_images and not original_images:
        print("❌ No images found in processed-imgs/ or images/ directories")
        print("Please run the PDF conversion demo first or add images to the images/ directory")
        return 1
    
    # Show available options
    print("=" * 60)
    print("OCR PROCESSING OPTIONS")
    print("=" * 60)
    
    if processed_images:
        print(f"📁 Processed Images Directory: {len(processed_images)} image(s)")
        for img in processed_images[:5]:  # Show first 5
            print(f"  - {img.name}")
        if len(processed_images) > 5:
            print(f"  ... and {len(processed_images) - 5} more")
    
    if original_images:
        print(f"\n📁 Original Images Directory: {len(original_images)} image(s)")
        for img in original_images[:5]:  # Show first 5
            print(f"  - {img.name}")
        if len(original_images) > 5:
            print(f"  ... and {len(original_images) - 5} more")
    
    print("\nProcessing Options:")
    print("  1. Process a single image from images/ directory")
    if processed_images:
        print("  2. Process all images in processed-imgs/ directory (batch)")
    print("  q. Quit")
    
    # Let user choose processing option
    while True:
        try:
            choice = input(f"\nChoose an option (1-{'2' if processed_images else '1'}, q): ").strip().lower()
            
            if choice == 'q':
                print("Demo cancelled.")
                return 0
            elif choice == '1':
                # Process single image from images/ directory
                if not original_images:
                    print("❌ No images found in images/ directory")
                    continue
                
                print(f"\nAvailable images in images/ directory:")
                for i, img_path in enumerate(original_images, 1):
                    print(f"  {i}. {img_path.name}")
                
                while True:
                    try:
                        img_choice = input(f"\nWhich image to process? (1-{len(original_images)}): ").strip()
                        if img_choice.lower() in ['q', 'quit', 'exit']:
                            return 0
                        
                        img_num = int(img_choice)
                        if 1 <= img_num <= len(original_images):
                            selected_image = original_images[img_num - 1]
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(original_images)}")
                    except ValueError:
                        print("Please enter a valid number")
                
                print(f"\nSelected: {selected_image.name}")
                
                # Run OCR demonstration
                results = demonstrate_ocr(selected_image)
                
                # Save results
                output_dir = Path(__file__).parent / "ocr-results"
                save_ocr_results(results, selected_image, output_dir)
                break
                
            elif choice == '2' and processed_images:
                # Process all images in processed-imgs/ directory
                print(f"\nProcessing all {len(processed_images)} images in processed-imgs/ directory...")
                
                # Create output directory
                output_dir = Path(__file__).parent / "ocr-results"
                output_dir.mkdir(exist_ok=True)
                
                # Process all images
                process_all_images(processed_images, output_dir)
                break
            else:
                print("Please enter a valid option")
        except ValueError:
            print("Please enter a valid option")
    
    # Explain PSM 3
    explain_psm3()
    
    print("\n" + "=" * 60)
    print("OCR DEMO COMPLETE!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
