#!/usr/bin/env python3
"""
Test Similarity Fix
==================

Test that different brands return poor matches
"""

import sys
import os

# Add the scraper directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper'))

from scraper.trolley_scraper import TrolleyScraper

def test_similarity():
    """Test similarity calculation for different brands"""
    print("🔧 TESTING SIMILARITY CALCULATION")
    print("=" * 60)
    
    scraper = TrolleyScraper(browser_profile="chrome120")
    
    # Test cases that should return poor matches
    test_cases = [
        # Test 3: Different brands (Kelloggs vs Tesco)
        ("Kelloggs Corn Flakes 500g", "Tesco Corn Flakes 500g"),
        
        # Test 4: Different brands (Heinz vs Asda)
        ("Heinz Tomato Ketchup 460g", "Asda Tomato Ketchup 460g"),
    ]
    
    for i, (name1, name2) in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}:")
        print(f"  Name 1: {name1}")
        print(f"  Name 2: {name2}")
        
        # Show brand extraction
        brand1, product1 = scraper._extract_brand_and_product(name1)
        brand2, product2 = scraper._extract_brand_and_product(name2)
        print(f"  Brand 1: '{brand1}'")
        print(f"  Brand 2: '{brand2}'")
        print(f"  Product 1: '{product1}'")
        print(f"  Product 2: '{product2}'")
        
        similarity = scraper._calculate_similarity(name1, name2)
        print(f"  Similarity Score: {similarity:.3f}")
        
        if similarity < 0.2:
            print(f"  ✅ POOR MATCH (as expected)")
        else:
            print(f"  ❌ UNEXPECTEDLY HIGH MATCH")
        
        print()

if __name__ == "__main__":
    test_similarity()
