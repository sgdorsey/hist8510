#!/usr/bin/env python3
"""
OCR Directory Cleanup Script
============================

This script resets the OCR demo directory back to its original state by removing
all generated files and directories from processing.

What gets removed:
- ocr-results/ directory and all .txt files
- processed-imgs/ directory and all processed images
- Any temporary files created during processing

What gets preserved:
- Original images in images/ directory
- PDF files in pdf/ directory
- Python scripts and configuration files
- README.md and requirements.txt

Usage:
    python cleanup.py
    python cleanup.py --dry-run    # Show what would be deleted without actually deleting
"""

import os
import sys
import shutil
from pathlib import Path
import argparse

def get_script_directory():
    """Get the directory where this script is located."""
    return Path(__file__).parent

def cleanup_directory(directory_path, dry_run=False):
    """
    Remove a directory and all its contents.
    
    Args:
        directory_path (Path): Path to directory to remove
        dry_run (bool): If True, only show what would be deleted
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not directory_path.exists():
        return True  # Directory doesn't exist, nothing to clean
    
    if dry_run:
        # Count files in directory
        file_count = len(list(directory_path.rglob('*')))
        print(f"  Would remove: {directory_path.name}/ ({file_count} files)")
        return True
    
    try:
        shutil.rmtree(directory_path)
        print(f"  ✅ Removed: {directory_path.name}/")
        return True
    except Exception as e:
        print(f"  ❌ Error removing {directory_path.name}/: {str(e)}")
        return False

def cleanup_files(file_patterns, dry_run=False):
    """
    Remove files matching specific patterns.
    
    Args:
        file_patterns (list): List of file patterns to remove
        dry_run (bool): If True, only show what would be deleted
    
    Returns:
        bool: True if successful, False otherwise
    """
    script_dir = get_script_directory()
    removed_count = 0
    
    for pattern in file_patterns:
        matching_files = list(script_dir.glob(pattern))
        
        for file_path in matching_files:
            if dry_run:
                print(f"  Would remove: {file_path.name}")
            else:
                try:
                    file_path.unlink()
                    print(f"  ✅ Removed: {file_path.name}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ Error removing {file_path.name}: {str(e)}")
    
    return True

def main():
    """Main cleanup function."""
    parser = argparse.ArgumentParser(
        description='Clean up OCR demo directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup.py              # Clean up the directory
  python cleanup.py --dry-run    # Show what would be deleted
        """
    )
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    script_dir = get_script_directory()
    
    print("=" * 60)
    print("OCR DIRECTORY CLEANUP")
    print("=" * 60)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will actually be deleted")
        print("-" * 50)
    else:
        print("🧹 Cleaning up OCR demo directory...")
        print("-" * 50)
    
    # Directories to remove
    directories_to_remove = [
        script_dir / "ocr-results",
        script_dir / "processed-imgs"
    ]
    
    # File patterns to remove (if any)
    file_patterns_to_remove = [
        "*.tmp",
        "*.log",
        "temp_*",
        "*.bak"
    ]
    
    # Processed files in images/ directory to remove
    processed_file_patterns = [
        "images/processed_*"
    ]
    
    success = True
    
    # Remove directories
    print("\nRemoving generated directories:")
    for directory in directories_to_remove:
        if not cleanup_directory(directory, args.dry_run):
            success = False
    
    # Remove temporary files
    print("\nRemoving temporary files:")
    cleanup_files(file_patterns_to_remove, args.dry_run)
    
    # Remove processed files from images/ directory
    print("\nRemoving processed files from images/ directory:")
    cleanup_files(processed_file_patterns, args.dry_run)
    
    # Show what's preserved
    print("\n" + "=" * 50)
    print("PRESERVED FILES AND DIRECTORIES:")
    print("=" * 50)
    
    preserved_items = [
        "images/ (original images only - processed_* files removed)",
        "pdf/ (PDF files)",
        "*.py (Python scripts)",
        "README.md",
        "requirements.txt"
    ]
    
    for item in preserved_items:
        print(f"  📁 {item}")
    
    # Summary
    print("\n" + "=" * 50)
    if args.dry_run:
        print("🔍 DRY RUN COMPLETE")
        print("Run without --dry-run to actually clean up the directory")
    else:
        if success:
            print("✅ CLEANUP COMPLETE!")
            print("The OCR demo directory has been reset to its original state.")
        else:
            print("⚠️  CLEANUP COMPLETED WITH WARNINGS")
            print("Some files may not have been removed successfully.")
    
    print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
