#!/usr/bin/env python3
"""
Quick multipack test
"""

from trolley_scraper_fixed import FixedTrolleyScraper

def quick_test():
    """Quick test for multipack fix"""
    print("🧪 Quick Multipack Test")
    print("=" * 30)
    
    scraper = FixedTrolleyScraper()
    
    # Test multipack detection
    test_cases = [
        "Heinz Cream of Tomato Soup 4 x 400g",
        "Heinz Baked Beans Family Pack",
        "Branston Baked Beans 4 x 410g"
    ]
    
    for product in test_cases:
        is_multipack = scraper._is_multipack(product)
        print(f"'{product}' -> Is multipack: {is_multipack}")
    
    # Test similarity calculation
    print("\n🔍 Testing similarity:")
    product1 = "Heinz Cream of Tomato Soup 4 x 400g"
    product2 = "Heinz Classic Cream of Tomato Soup Family Pack"
    similarity = scraper._calculate_similarity_improved(product1, product2)
    print(f"Similarity between '{product1}' and '{product2}': {similarity:.3f}")

if __name__ == "__main__":
    quick_test()
