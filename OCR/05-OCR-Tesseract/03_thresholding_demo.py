#!/usr/bin/env python3
"""
Demo 3: Thresholding and Binarization for Historical Documents
=============================================================

This demo shows different thresholding techniques for converting
grayscale images to binary (black and white) for OCR:

- Simple Thresholding
- Adaptive Thresholding
- Otsu's Method
- Triangle Method

Run this script to see how different thresholding methods handle
varying lighting conditions in historical documents.
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

def apply_simple_threshold(image, threshold_value=127):
    """Apply simple thresholding."""
    _, binary = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
    print(f"✓ Applied simple threshold (threshold={threshold_value})")
    return binary

def apply_adaptive_threshold_gaussian(image, block_size=11, C=2):
    """Apply adaptive thresholding using Gaussian method."""
    binary = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, C
    )
    print(f"✓ Applied adaptive threshold (Gaussian, block_size={block_size}, C={C})")
    return binary

def apply_adaptive_threshold_mean(image, block_size=11, C=2):
    """Apply adaptive thresholding using mean method."""
    binary = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, C
    )
    print(f"✓ Applied adaptive threshold (Mean, block_size={block_size}, C={C})")
    return binary

def apply_otsu_threshold(image):
    """Apply Otsu's automatic thresholding method."""
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    print("✓ Applied Otsu's thresholding (automatic)")
    return binary

def apply_triangle_threshold(image):
    """Apply Triangle method thresholding."""
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)
    print("✓ Applied Triangle thresholding")
    return binary

def create_comparison_plot(original, processed_images, titles, save_path=None):
    """Create a comparison plot showing original and processed images."""
    n_images = len(processed_images) + 1  # +1 for original
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    # Show original
    axes[0].imshow(original, cmap='gray')
    axes[0].set_title('Original Grayscale', fontsize=12, fontweight='bold')
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
    plt.suptitle('Thresholding Techniques Comparison', fontsize=16, fontweight='bold', y=0.98)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Comparison plot saved to: {save_path}")
    
    plt.show()

def create_histogram_with_thresholds(image, thresholds, save_path=None):
    """Create histogram showing different threshold values."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Create histogram
    hist, bins = np.histogram(image.ravel(), bins=256, range=[0, 256])
    ax.plot(bins[:-1], hist, color='blue', alpha=0.7, label='Histogram')
    
    # Add threshold lines
    colors = ['red', 'green', 'orange', 'purple', 'brown']
    threshold_names = ['Simple (127)', 'Otsu', 'Triangle', 'Adaptive Gaussian', 'Adaptive Mean']
    
    for i, (threshold, name) in enumerate(zip(thresholds, threshold_names)):
        if threshold is not None:
            ax.axvline(x=threshold, color=colors[i % len(colors)], 
                      linestyle='--', linewidth=2, label=f'{name} ({threshold})')
    
    ax.set_xlabel('Pixel Intensity')
    ax.set_ylabel('Frequency')
    ax.set_title('Histogram with Threshold Values', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Histogram with thresholds saved to: {save_path}")
    
    plt.show()

def demonstrate_thresholding(image_path):
    """Demonstrate different thresholding techniques."""
    print("=" * 60)
    print("THRESHOLDING DEMONSTRATION")
    print("=" * 60)
    
    # Load image
    image = load_image(image_path)
    
    # Convert to grayscale
    gray = convert_to_grayscale(image)
    
    print("\nApplying different thresholding techniques...")
    print("-" * 50)
    
    # Apply different thresholding techniques
    simple_thresh = apply_simple_threshold(gray, threshold_value=127)
    adaptive_gaussian = apply_adaptive_threshold_gaussian(gray, block_size=11, C=2)
    adaptive_mean = apply_adaptive_threshold_mean(gray, block_size=11, C=2)
    otsu_thresh = apply_otsu_threshold(gray)
    triangle_thresh = apply_triangle_threshold(gray)
    
    # Get threshold values for histogram
    _, otsu_threshold_value = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, triangle_threshold_value = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)
    
    thresholds = [127, otsu_threshold_value, triangle_threshold_value, None, None]
    
    # Create comparison
    processed_images = [simple_thresh, adaptive_gaussian, adaptive_mean, otsu_thresh, triangle_thresh]
    titles = [
        'Simple Threshold\n(127)',
        'Adaptive Gaussian\n(block_size=11)',
        'Adaptive Mean\n(block_size=11)',
        'Otsu\'s Method\n(Automatic)',
        'Triangle Method\n(Automatic)'
    ]
    
    # Save individual results to images/ directory with prefix
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    images_dir = Path(__file__).parent / "images"
    images_dir.mkdir(exist_ok=True)
    
    cv2.imwrite(str(images_dir / f"processed_{base_name}_simple_thresh.png"), simple_thresh)
    cv2.imwrite(str(images_dir / f"processed_{base_name}_adaptive_gaussian.png"), adaptive_gaussian)
    cv2.imwrite(str(images_dir / f"processed_{base_name}_adaptive_mean.png"), adaptive_mean)
    cv2.imwrite(str(images_dir / f"processed_{base_name}_otsu.png"), otsu_thresh)
    cv2.imwrite(str(images_dir / f"processed_{base_name}_triangle.png"), triangle_thresh)
    
    print(f"\n✓ Saved individual results for {os.path.basename(image_path)}")
    
    # Create comparison plot in images/ directory
    comparison_path = images_dir / f"processed_thresholding_comparison_{base_name}.png"
    create_comparison_plot(gray, processed_images, titles, save_path=str(comparison_path))
    
    # Create histogram with thresholds in images/ directory
    histogram_path = images_dir / f"processed_threshold_histogram_{base_name}.png"
    create_histogram_with_thresholds(gray, thresholds, save_path=str(histogram_path))
    
    return gray, processed_images, titles

def explain_techniques():
    """Print explanation of different thresholding techniques."""
    print("\n" + "=" * 60)
    print("THRESHOLDING TECHNIQUES EXPLAINED")
    print("=" * 60)
    
    print("""
1. SIMPLE THRESHOLDING
   - Uses a fixed threshold value
   - All pixels above threshold become white, below become black
   - Simple but may not work well with varying lighting
   - Best for: Images with consistent lighting

2. ADAPTIVE THRESHOLDING
   - Calculates threshold for small regions of the image
   - Two methods: Gaussian and Mean
   - Handles varying lighting conditions
   - Best for: Documents with shadows or uneven lighting

3. OTSU'S METHOD
   - Automatically determines optimal threshold
   - Minimizes intra-class variance
   - Works well for bimodal histograms
   - Best for: Images with clear foreground/background separation

4. TRIANGLE METHOD
   - Finds threshold at maximum distance from diagonal
   - Good for images with dominant background
   - Automatic threshold selection
   - Best for: Documents with mostly white background

PARAMETERS EXPLAINED:
- block_size: Size of neighborhood for adaptive thresholding
- C: Constant subtracted from mean (adaptive thresholding)
- threshold_value: Fixed threshold for simple thresholding

WHEN TO USE EACH:
- Simple: Quick processing, consistent lighting
- Adaptive: Varying lighting, shadows
- Otsu: Automatic, bimodal histograms
- Triangle: Automatic, dominant background
""")

def main():
    """Main function to run the thresholding demo."""
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
    print("THRESHOLDING DEMO")
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
        demonstrate_thresholding(str(selected_image))
        
        # Explain techniques after processing
        explain_techniques()
        
        print("\n" + "=" * 60)
        print("THRESHOLDING DEMO COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error processing {selected_image.name}: {str(e)}")

if __name__ == "__main__":
    main()
