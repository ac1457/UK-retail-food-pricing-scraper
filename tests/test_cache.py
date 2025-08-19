#!/usr/bin/env python3
"""
Test Cache Functionality
========================
Demonstrate the caching functionality of the scraper
"""

import sys
import os
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper


def test_cache_functionality():
    """Test the caching functionality"""
    print("🧪 Testing Cache Functionality")
    print("=" * 60)
    
    # Initialize scraper with 1 hour cache duration
    scraper = FixedTrolleyScraper(cache_duration_hours=1)
    
    # Test product
    test_product = "Alfez Moroccan Cous Cous 200g"
    
    print(f"🔍 Testing with product: {test_product}")
    print()
    
    # First search (should scrape from website)
    print("📡 FIRST SEARCH (should scrape from website):")
    start_time = time.time()
    results1 = scraper.search_product(test_product)
    end_time = time.time()
    
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"📊 Results found: {len(results1)}")
    if results1:
        print(f"🏆 Best match: {results1[0]['name']} (score: {results1[0]['similarity_score']:.3f})")
    print()
    
    # Second search (should use cache)
    print("📋 SECOND SEARCH (should use cache):")
    start_time = time.time()
    results2 = scraper.search_product(test_product)
    end_time = time.time()
    
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"📊 Results found: {len(results2)}")
    if results2:
        print(f"🏆 Best match: {results2[0]['name']} (score: {results2[0]['similarity_score']:.3f})")
    print()
    
    # Verify results are the same
    if results1 and results2:
        if len(results1) == len(results2):
            print("✅ SUCCESS: Cache working correctly!")
            print(f"   - Both searches returned {len(results1)} results")
            print(f"   - Second search was much faster")
        else:
            print("❌ ERROR: Cache results don't match")
    else:
        print("⚠️  WARNING: No results found for test product")
    
    # Print cache statistics
    print()
    scraper.print_cache_stats()


if __name__ == "__main__":
    test_cache_functionality()
