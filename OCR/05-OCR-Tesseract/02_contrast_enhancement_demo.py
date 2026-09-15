#!/usr/bin/env python3
"""
Demo 2: Contrast Enhancement for Historical Documents
====================================================

This demo shows how to enhance contrast in historical documents using:
- Histogram Equalization (Global)
- CLAHE (Contrast Limited Adaptive Histogram Equalization)
- Gamma Correction
- Unsharp Masking

Run this script to see how different contrast enhancement techniques
affect faded or low-contrast historical documents.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

def load_image(image_path):
    """Load and display image information."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    print(f"Loaded: {os.path.basename(image_path)}")
    print(f"Image shape: {image.shape}")
    
    return image

def convert_to_grayscale(image):
    """Convert BGR image to grayscale."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("✓ Converted to grayscale")
    return gray

def apply_histogram_equalization(image):
    """Apply global histogram equalization."""
    equalized = cv2.equalizeHist(image)
    print("✓ Applied global histogram equalization")
    return equalized

def apply_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    clahe_image = clahe.apply(image)
    print(f"✓ Applied CLAHE (clip_limit={clip_limit}, tile_size={tile_grid_size})")
    return clahe_image

def apply_gamma_correction(image, gamma=1.2):
    """Apply gamma correction."""
    # Build lookup table
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
    gamma_corrected = cv2.LUT(image, table)
    print(f"✓ Applied gamma correction (γ={gamma})")
    return gamma_corrected

def apply_unsharp_masking(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Apply unsharp masking to enhance text sharpness."""
    # Create Gaussian kernel
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    
    print(f"✓ Applied unsharp masking (amount={amount}, σ={sigma})")
    return sharpened

def create_histogram_comparison(images, titles, save_path=None):
    """Create histogram comparison for contrast analysis."""
    fig, axes = plt.subplots(2, len(images), figsize=(15, 8))
    
    if len(images) == 1:
        axes = axes.reshape(2, 1)
    
    for i, (img, title) in enumerate(zip(images, titles)):
        # Show image
        axes[0, i].imshow(img, cmap='gray')
        axes[0, i].set_title(title, fontsize=10)
        axes[0, i].axis('off')
        
        # Show histogram
        axes[1, i].hist(img.ravel(), bins=256, range=[0, 256], alpha=0.7, color='blue')
        axes[1, i].set_title(f'Histogram - {title}', fontsize=10)
        axes[1, i].set_xlabel('Pixel Intensity')
        axes[1, i].set_ylabel('Frequency')
        axes[1, i].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.suptitle('Contrast Enhancement: Images and Histograms', fontsize=14, fontweight='bold', y=0.98)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Histogram comparison saved to: {save_path}")
    
    plt.show()

def create_comparison_plot(original, processed_images, titles, save_path=None):
    """Create a comparison plot showing original and processed images."""
    n_images = len(processed_images) + 1  # +1 for original
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    # Show original
    axes[0].imshow(original, cmap='gray')
    axes[0].set_title('Original Image', fontsize=12, fontweight='bold')
    axes[0].axis('off')
    
    # Show processed images
    for i, (img, title) in enumerate(zip(processed_images, titles)):
        axes[i + 1].imshow(img, cmap='gray')
        axes[i + 1].set_title(title, fontsize=12)
        axes[i + 1].axis('off')
    
    # Hide unused subplots
    for i in range(n_images, len(axes)):
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.suptitle('Contrast Enhancement Techniques Comparison', fontsize=16, fontweight='bold', y=0.98)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Comparison plot saved to: {save_path}")
    
    plt.show()

def demonstrate_contrast_enhancement(image_path):
    """Demonstrate different contrast enhancement techniques."""
    print("=" * 60)
    print("CONTRAST ENHANCEMENT DEMONSTRATION")
    print("=" * 60)
    
    # Load image
    image = load_image(image_path)
    
    # Convert to grayscale
    gray = convert_to_grayscale(image)
    
    print("\nApplying different contrast enhancement techniques...")
    print("-" * 50)
    
    # Apply different contrast enhancement techniques
    histogram_eq = apply_histogram_equalization(gray)
    clahe_enhanced = apply_clahe(gray, clip_limit=2.0, tile_grid_size=(8, 8))
    gamma_corrected = apply_gamma_correction(gray, gamma=1.2)
    unsharp_masked = apply_unsharp_masking(gray, amount=1.0, sigma=1.0)
    
    # Create comparison
    processed_images = [histogram_eq, clahe_enhanced, gamma_corrected, unsharp_masked]
    titles = [
        'Global Histogram\nEqualization',
        'CLAHE\n(Adaptive)',
        'Gamma Correction\n(γ=1.2)',
        'Unsharp Masking\n(Sharpening)'
    ]
    
    # Save individual results to images/ directory with prefix
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    images_dir = Path(__file__).parent / "images"
    images_dir.mkdir(exist_ok=True)
    
    cv2.imwrite(str(images_dir / f"processed_{base_name}_histogram_eq.png"), histogram_eq)
    cv2.imwrite(str(images_dir / f"processed_{base_name}_clahe.png"), clahe_enhanced)
    cv2.imwrite(str(images_dir / f"processed_{base_name}_gamma.png"), gamma_corrected)
    cv2.imwrite(str(images_dir / f"processed_{base_name}_unsharp.png"), unsharp_masked)
    
    print(f"\n✓ Saved individual results for {os.path.basename(image_path)}")
    
    # Create comparison plot in images/ directory
    comparison_path = images_dir / f"processed_contrast_enhancement_comparison_{base_name}.png"
    create_comparison_plot(gray, processed_images, titles, save_path=str(comparison_path))
    
    # Create histogram comparison in images/ directory
    all_images = [gray] + processed_images
    all_titles = ['Original'] + titles
    histogram_path = images_dir / f"processed_histogram_comparison_{base_name}.png"
    create_histogram_comparison(all_images, all_titles, save_path=str(histogram_path))
    
    return gray, processed_images, titles

def explain_techniques():
    """Print explanation of different contrast enhancement techniques."""
    print("\n" + "=" * 60)
    print("CONTRAST ENHANCEMENT TECHNIQUES EXPLAINED")
    print("=" * 60)
    
    print("""
1. GLOBAL HISTOGRAM EQUALIZATION
   - Spreads pixel intensities across the full range
   - Can over-enhance some areas
   - May lose local details
   - Best for: Images with poor global contrast

2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
   - Applies histogram equalization to small regions
   - Limits contrast enhancement to avoid over-amplification
   - Preserves local details better
   - Best for: Images with varying local contrast

3. GAMMA CORRECTION
   - Adjusts brightness and contrast using power law
   - γ < 1: Brightens image, increases contrast in dark areas
   - γ > 1: Darkens image, increases contrast in bright areas
   - Best for: Fine-tuning brightness and contrast

4. UNSHARP MASKING
   - Enhances edges and fine details
   - Subtracts blurred version from original
   - Makes text appear sharper
   - Best for: Enhancing text readability

WHEN TO USE EACH:
- Global Histogram Eq: Quick global contrast improvement
- CLAHE: When you have varying lighting across the document
- Gamma Correction: When you need fine control over brightness
- Unsharp Masking: When text appears blurry or soft
""")

def main():
    """Main function to run the contrast enhancement demo."""
    images_dir = Path(__file__).parent / "images"
    
    if not images_dir.exists():
        print(f"Images directory not found: {images_dir}")
        return
    
    # Get all image files
    image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg"))
    
    if not image_files:
        print("No image files found in the images directory")
        return
    
    print(f"Found {len(image_files)} image(s) available:")
    for i, img_file in enumerate(image_files, 1):
        print(f"  {i}. {img_file.name}")
    
    print("\n" + "=" * 60)
    print("CONTRAST ENHANCEMENT DEMO")
    print("=" * 60)
    
    # Let user choose which image to process
    while True:
        try:
            choice = input(f"\nWhich image would you like to process? (1-{len(image_files)}): ").strip()
            if choice.lower() in ['q', 'quit', 'exit']:
                print("Demo cancelled.")
                return
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(image_files):
                selected_image = image_files[choice_num - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(image_files)}")
        except ValueError:
            print("Please enter a valid number")
    
    print(f"\nSelected: {selected_image.name}")
    print("-" * 50)
    
    try:
        demonstrate_contrast_enhancement(str(selected_image))
        
        # Explain techniques after processing
        explain_techniques()
        
        print("\n" + "=" * 60)
        print("CONTRAST ENHANCEMENT DEMO COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error processing {selected_image.name}: {str(e)}")

if __name__ == "__main__":
    main()
