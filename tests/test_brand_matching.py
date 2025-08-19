#!/usr/bin/env python3
"""
Test brand matching improvements
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper

def test_brand_matching():
    """Test brand matching logic"""
    print("🧪 Testing brand matching improvements")
    print("=" * 50)
    
    # Initialize scraper
    scraper = FixedTrolleyScraper()
    
    # Test cases
    test_cases = [
        # Should NOT match (different brands)
        ("Daddies Brown Sauce", "HP Brown Sauce"),
        ("Heinz Baked Beans", "Branston Baked Beans"),
        ("Al'Fez Couscous", "Tesco Couscous"),
        ("Dr. Oetker Pizza", "Goodfella's Pizza"),
        
        # Should match (same brand variations)
        ("Al'Fez Couscous", "Al-Fez Couscous"),
        ("Dr. Oetker Pizza", "Dr Oetker Pizza"),
        ("Coca Cola", "Coca-Cola"),
        ("Sainsburys Beans", "Sainsbury Beans"),
    ]
    
    print("🔍 Testing brand similarity:")
    for product1, product2 in test_cases:
        brand1, _ = scraper._extract_brand_and_product(product1)
        brand2, _ = scraper._extract_brand_and_product(product2)
        
        are_similar = scraper._are_brands_similar(brand1, brand2)
        similarity = scraper._calculate_similarity_improved(product1, product2)
        
        print(f"\n  {product1} vs {product2}")
        print(f"    Brand1: '{brand1}' | Brand2: '{brand2}'")
        print(f"    Similar brands: {are_similar}")
        print(f"    Overall similarity: {similarity:.3f}")
        
        # Check if this should match or not
        if "NOT match" in product1 or "NOT match" in product2:
            if similarity > 0.1:
                print(f"    ❌ ERROR: Should NOT match but similarity is {similarity:.3f}")
            else:
                print(f"    ✅ CORRECT: Correctly rejected (similarity: {similarity:.3f})")
        else:
            if similarity > 0.3:
                print(f"    ✅ CORRECT: Should match (similarity: {similarity:.3f})")
            else:
                print(f"    ❌ ERROR: Should match but similarity is too low: {similarity:.3f}")

if __name__ == "__main__":
    test_brand_matching()
