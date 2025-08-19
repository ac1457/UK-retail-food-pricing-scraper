#!/usr/bin/env python3
"""
Workflow Cleanup Script
======================
Clean up unused files and keep only the essential workflow files
"""

import os
import shutil
import sys

def cleanup_workflow():
    """Clean up the workflow by removing unused files"""
    print("🧹 Cleaning up workflow files...")
    print("=" * 60)
    
    # Essential files to keep
    essential_files = {
        # Core workflow files
        'final_fixed_workflow.py',
        'manage_cache.py',
        'README.md',
        'requirements.txt',
        'main.py',
        'LICENSE',
        '.gitignore',
        'pytest.ini',
        'pyproject.toml',
        '.flake8',
        '.gitattributes',
        
        # Core scraper files
        'scraper/trolley_scraper_fixed.py',
        'scraper/cache_manager.py',
        'scraper/constants.py',
        'scraper/filemanager.py',
        'scraper/settings.ini',
        'scraper/__init__.py',
        
        # Test files (keep only the most useful ones)
        'test_workflow_multipack.py',
        'test_cache.py',
        'debug_heinz_multipack_price.py',
        'quick_price_test.py',
        
        # Your Excel file
        'Pricing Exp_final_fixed.xlsx',
    }
    
    # Files to remove (debug, test, and temporary files)
    files_to_remove = [
        # Debug files
        'debug_alfez_specific.py',
        'debug_alfez_search.py',
        'debug_alfez_search_only.py',
        'debug_alfez_similarity.py',
        'debug_brand_similarity.py',
        'debug_card_extraction.py',
        'debug_full_similarity.py',
        'debug_moroccan_search.py',
        'debug_moroccan_similarity.py',
        'debug_similarity.py',
        
        # Test files (keep only essential ones)
        'test_heinz_multipack.py',
        'test_multipack_matching.py',
        'test_known_products.py',
        'test_simple_searches.py',
        'test_new_scraper_direct.py',
        'test_final_fixed_workflow.py',
        'test_fixed_workflow.py',
        'test_updated_workflow.py',
        'test_strict_matching.py',
        'test_quantity_tolerance.py',
        'test_improved_search.py',
        'test_trolley_fix.py',
        'test_trolley_scraper.py',
        'test_max_accuracy.py',
        'test_improved_accuracy.py',
        'test_similarity_fix.py',
        'test_tesco_fix.py',
        'run_test_workflow.py',
        'test_config.py',
        'test_workflow_prototype.py',
        'test_your_excel.py',
        'run_trolley_workflow.py',
        'fix_workflow_issues.py',
        
        # Old scraper files
        'scraper/trolley_scraper.py',
        'scraper/trolley_bulk_import.py',
        'scraper/enhanced_bulk_import.py',
        'scraper/bulk_import.py',
        'scraper/enhanced_custom_bulk_import.py',
        'scraper/custom_bulk_import.py',
        'scraper/excel_output_generator.py',
        'scraper/custom_bulk_import_functions.py',
        'scraper/custom_excel_processor.py',
        'scraper/bulk_import_functions.py',
        
        # Test Excel files
        'test_final_fixed_results.xlsx',
        'test_products_final.xlsx',
        'test_fixed_results.xlsx',
        
        # Log files
        'test_workflow_20250813_172755.log',
        'test_workflow_20250813_131332.log',
        'test_workflow_20250813_130753.log',
        'scraper/logfile.log',
        
        # Documentation files (keep only main README)
        'TEST_WORKFLOW_README.md',
        'YOUR_EXCEL_GUIDE.md',
        'UK_ECOMMERCE_GUIDE.md',
        
        # Other utility files
        'create_sample_excel.py',
    ]
    
    # Directories to clean up
    dirs_to_clean = [
        'test_logs',
        'test_outputs',
        '__pycache__',
        'scraper/__pycache__',
    ]
    
    removed_files = []
    removed_dirs = []
    
    # Remove files
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                removed_files.append(file_path)
                print(f"🗑️  Removed: {file_path}")
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
    
    # Clean up directories
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                removed_dirs.append(dir_path)
                print(f"🗑️  Removed directory: {dir_path}")
            except Exception as e:
                print(f"❌ Failed to remove directory {dir_path}: {e}")
    
    # Keep cache directory but clean old files
    if os.path.exists('cache'):
        print(f"📋 Cache directory kept (contains cached data)")
    
    print(f"\n✅ Cleanup completed!")
    print(f"📁 Removed {len(removed_files)} files")
    print(f"📁 Removed {len(removed_dirs)} directories")
    
    # Show remaining essential files
    print(f"\n📋 Essential files remaining:")
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
    
    print(f"\n🎯 Your workflow is now clean!")
    print(f"   Main workflow: final_fixed_workflow.py")
    print(f"   Cache management: manage_cache.py")
    print(f"   Core scraper: scraper/trolley_scraper_fixed.py")
    print(f"   Cache system: scraper/cache_manager.py")


if __name__ == "__main__":
    cleanup_workflow()
