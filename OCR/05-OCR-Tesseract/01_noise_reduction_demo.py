#!/usr/bin/env python3
"""
Demo 1: Noise Reduction for Historical Documents
===============================================

This demo shows how to reduce noise in historical documents using:
- Gaussian blur
- Median filtering
- Bilateral filtering

Run this script to see the effects of different noise reduction techniques.
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
    print(f"Image type: {image.dtype}")
    
    return image

def convert_to_grayscale(image):
    """Convert BGR image to grayscale."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("✓ Converted to grayscale")
    return gray

def apply_gaussian_blur(image, kernel_size=5):
    """Apply Gaussian blur for noise reduction."""
    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    print(f"✓ Applied Gaussian blur (kernel size: {kernel_size})")
    return blurred

def apply_median_filter(image, kernel_size=5):
    """Apply median filter for noise reduction."""
    median = cv2.medianBlur(image, kernel_size)
    print(f"✓ Applied median filter (kernel size: {kernel_size})")
    return median

def apply_bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """Apply bilateral filter for edge-preserving noise reduction."""
    bilateral = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    print(f"✓ Applied bilateral filter (d={d}, σ_color={sigma_color}, σ_space={sigma_space})")
    return bilateral

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
    plt.suptitle('Noise Reduction Techniques Comparison', fontsize=16, fontweight='bold', y=0.98)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Comparison plot saved to: {save_path}")
    
    plt.show()

def demonstrate_noise_reduction(image_path):
    """Demonstrate different noise reduction techniques."""
    print("=" * 60)
    print("NOISE REDUCTION DEMONSTRATION")
    print("=" * 60)
    
    # Load image
    image = load_image(image_path)
    
    # Convert to grayscale
    gray = convert_to_grayscale(image)
    
    print("\nApplying different noise reduction techniques...")
    print("-" * 50)
    
    # Apply different noise reduction techniques
    gaussian_blur = apply_gaussian_blur(gray, kernel_size=5)
    median_filter = apply_median_filter(gray, kernel_size=5)
    bilateral_filter = apply_bilateral_filter(gray, d=9, sigma_color=75, sigma_space=75)
    
    # Create comparison
    processed_images = [gaussian_blur, median_filter, bilateral_filter]
    titles = [
        'Gaussian Blur\n(Good for general noise)',
        'Median Filter\n(Good for salt & pepper noise)',
        'Bilateral Filter\n(Edge-preserving)'
    ]
    
    # Save individual results to images/ directory with prefix
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    images_dir = Path(__file__).parent / "images"
    images_dir.mkdir(exist_ok=True)
    
    cv2.imwrite(str(images_dir / f"processed_{base_name}_gaussian_blur.png"), gaussian_blur)
    cv2.imwrite(str(images_dir / f"processed_{base_name}_median_filter.png"), median_filter)
    cv2.imwrite(str(images_dir / f"processed_{base_name}_bilateral_filter.png"), bilateral_filter)
    
    print(f"\n✓ Saved individual results for {os.path.basename(image_path)}")
    
    # Create comparison plot in images/ directory
    comparison_path = images_dir / f"processed_noise_reduction_comparison_{base_name}.png"
    create_comparison_plot(gray, processed_images, titles, save_path=str(comparison_path))
    
    return gray, processed_images, titles

def explain_techniques():
    """Print explanation of different noise reduction techniques."""
    print("\n" + "=" * 60)
    print("NOISE REDUCTION TECHNIQUES EXPLAINED")
    print("=" * 60)
    
    print("""
1. GAUSSIAN BLUR
   - Uses a Gaussian kernel to blur the image
   - Reduces high-frequency noise effectively
   - May blur important text details
   - Best for: General noise reduction

2. MEDIAN FILTER
   - Replaces each pixel with the median of neighboring pixels
   - Excellent for salt-and-pepper noise
   - Preserves edges better than Gaussian blur
   - Best for: Impulse noise, speckles

3. BILATERAL FILTER
   - Combines spatial and intensity information
   - Reduces noise while preserving edges
   - More computationally expensive
   - Best for: Edge-preserving noise reduction

WHEN TO USE EACH:
- Gaussian Blur: Quick general noise reduction
- Median Filter: When you have salt-and-pepper noise
- Bilateral Filter: When you need to preserve text edges
""")

def main():
    """Main function to run the noise reduction demo."""
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
    print("NOISE REDUCTION DEMO")
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
        demonstrate_noise_reduction(str(selected_image))
        
        # Explain techniques after processing
        explain_techniques()
        
        print("\n" + "=" * 60)
        print("NOISE REDUCTION DEMO COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error processing {selected_image.name}: {str(e)}")

if __name__ == "__main__":
    main()
