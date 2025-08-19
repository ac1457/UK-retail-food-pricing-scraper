#!/usr/bin/env python3
"""
Test Alfez vs Co-op Similarity
==============================

Test that Alfez products don't match with Co-op products
"""

import sys
import os

# Add the scraper directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper'))

from scraper.trolley_scraper import TrolleyScraper

def test_alfez_vs_coop():
    """Test that Alfez products don't match with Co-op products"""
    print("🔧 TESTING ALFEZ VS CO-OP SIMILARITY")
    print("=" * 60)
    
    scraper = TrolleyScraper(browser_profile="chrome120")
    
    # Test the specific case from the user
    test_cases = [
        # Original search vs found product
        ("Alfez Moroccan Cous Cous 200g", "Co-op Moroccan Cous Cous 215g"),
        
        # Other variations
        ("Alfez Moroccan Cous Cous 200g", "Co-op Moroccan Style Cous Cous 215g"),
        ("Alfez Moroccan Cous Cous 200g", "Co-op Moroccan Cous Cous"),
        
        # Should match (same brand, similar product)
        ("Alfez Moroccan Cous Cous 200g", "Alfez Moroccan Cous Cous 215g"),
        ("Alfez Moroccan Cous Cous 200g", "Al-fez Moroccan Cous Cous 200g"),
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
        
        if similarity < 0.1:
            print(f"  ✅ POOR MATCH (correct)")
        elif similarity >= 0.4:
            print(f"  ✅ GOOD MATCH (correct)")
        else:
            print(f"  ⚠️  MODERATE MATCH")
        
        print()

if __name__ == "__main__":
    test_alfez_vs_coop()
