#!/usr/bin/env python3
"""
Simple test for Heinz multipack fix
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper

def test_heinz_fix():
    """Test the Heinz multipack fix"""
    print("🧪 Testing Heinz multipack fix")
    print("=" * 40)
    
    # Initialize scraper
    scraper = FixedTrolleyScraper()
    scraper.clear_cache()
    
    # Test the specific problematic text
    test_text = "415g6Heinz Baked Beans1 13 more sizes"
    cleaned = scraper._clean_extracted_name(test_text)
    print(f"Original: {test_text}")
    print(f"Cleaned:  {cleaned}")
    
    # Test similarity calculation
    original_product = "Heinz Beanz 6 x 415g"
    similarity = scraper._calculate_similarity_improved(cleaned, original_product)
    print(f"Similarity with '{original_product}': {similarity:.3f}")
    
    # Test if it would be accepted
    if similarity >= 0.15:
        print("✅ Would be accepted by scraper")
    else:
        print("❌ Would be rejected by scraper")

if __name__ == "__main__":
    test_heinz_fix()
