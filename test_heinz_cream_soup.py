#!/usr/bin/env python3
"""
Test Heinz Cream of Tomato Soup multipack issue
"""

from trolley_scraper_fixed import FixedTrolleyScraper

def test_heinz_cream_soup():
    """Test Heinz Cream of Tomato Soup multipack matching"""
    print("🧪 Testing Heinz Cream of Tomato Soup Multipack")
    print("=" * 55)
    
    scraper = FixedTrolleyScraper()
    scraper.clear_cache()
    
    # Test the problematic product
    product = "Heinz Cream of Tomato Soup 4 x 400g"
    print(f"🔍 Testing: {product}")
    
    # Check if it's detected as multipack
    is_multipack = scraper._is_multipack(product)
    print(f"   Is multipack: {is_multipack}")
    
    # Check quantity extraction
    quantity, pack_size = scraper._extract_quantity_and_pack_size(product)
    print(f"   Quantity: {quantity}, Pack size: {pack_size}")
    
    # Check brand extraction
    brand, product_name = scraper._extract_brand_and_product(product)
    print(f"   Brand: '{brand}', Product: '{product_name}'")
    
    # Test similarity with the found product
    found_product = "Heinz Classic Cream of Tomato Soup Family Pack"
    similarity = scraper._calculate_similarity_improved(found_product, product)
    print(f"   Similarity with '{found_product}': {similarity:.3f}")
    
    # Check if found product is multipack
    found_is_multipack = scraper._is_multipack(found_product)
    print(f"   Found product is multipack: {found_is_multipack}")
    
    # Test actual search
    results = scraper.search_product(product)
    
    if results:
        print(f"   ✅ Found {len(results)} results")
        for i, result in enumerate(results[:3], 1):  # Show top 3
            print(f"     {i}. {result['name']} (Score: {result['similarity_score']:.3f})")
            print(f"        URL: {result['url']}")
            print(f"        Is multipack: {scraper._is_multipack(result['name'])}")
        
        best = max(results, key=lambda x: x['similarity_score'])
        print(f"   🏆 Best match: {best['name']} (Score: {best['similarity_score']:.3f})")
        print(f"      URL: {best['url']}")
        
        # Check if it's a multipack match
        if scraper._is_multipack(best['name']):
            print(f"      ✅ Correctly matched multipack")
        else:
            print(f"      ❌ ERROR: Matched single product instead of multipack!")
    else:
        print(f"   ❌ No results found")

if __name__ == "__main__":
    test_heinz_cream_soup()
