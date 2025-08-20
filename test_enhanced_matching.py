#!/usr/bin/env python3
"""
Test Enhanced Product Matching System
====================================

Tests the enhanced product matching functionality with various scenarios
"""

import asyncio
from enhanced_matcher import EnhancedProductMatcher, ProductMatch, MLProductMatcher
from enhanced_scraper import EnhancedScraper


def test_text_cleaning():
    """Test the text cleaning functionality"""
    print("🧪 Testing Text Cleaning")
    print("=" * 40)
    
    matcher = EnhancedProductMatcher()
    
    test_cases = [
        "Heinz Baked Beans 415g 2x Clubcard Price",
        "Tesco Baked Beans 420g Special Offer",
        "Branston Baked Beans 410g 3 for £2",
        "Heinz Cream of Tomato Soup 400g New Formula",
    ]
    
    for text in test_cases:
        cleaned = matcher.clean_product_text(text)
        print(f"Original: {text}")
        print(f"Cleaned:  {cleaned}")
        print()


def test_weight_extraction():
    """Test weight/volume extraction"""
    print("🧪 Testing Weight/Volume Extraction")
    print("=" * 40)
    
    matcher = EnhancedProductMatcher()
    
    test_cases = [
        "Heinz Baked Beans 415g",
        "Tesco Milk 2.272L",
        "Branston Pickle 454g",
        "Heinz Soup 400ml",
        "Eggs 6 Pack",
        "Bread 800g",
    ]
    
    for text in test_cases:
        weight, unit = matcher.extract_weight_volume(text)
        print(f"Text: {text}")
        print(f"Weight: {weight}, Unit: {unit}")
        print()


def test_brand_extraction():
    """Test brand and product extraction"""
    print("🧪 Testing Brand Extraction")
    print("=" * 40)
    
    matcher = EnhancedProductMatcher()
    
    test_cases = [
        "Heinz Baked Beans 415g",
        "Tesco Baked Beans 420g",
        "Branston Pickle 454g",
        "Sainsbury's Baked Beans 410g",
        "ASDA Milk 2.272L",
    ]
    
    for text in test_cases:
        brand, product = matcher.extract_brand_and_product(text)
        print(f"Text: {text}")
        print(f"Brand: {brand}")
        print(f"Product: {product}")
        print()


def test_similarity_matching():
    """Test similarity matching between products"""
    print("🧪 Testing Similarity Matching")
    print("=" * 40)
    
    matcher = EnhancedProductMatcher()
    
    # Test cases with expected high similarity
    test_pairs = [
        ("Heinz Baked Beans 415g", "Heinz Baked Beans 415g"),  # Exact match
        ("Heinz Baked Beans 415g", "Heinz Baked Beans 420g"),  # Same brand, similar weight
        ("Heinz Baked Beans 415g", "Tesco Baked Beans 420g"),  # Different brand, same product
        ("Heinz Baked Beans 415g", "Branston Baked Beans 410g"),  # Different brand, same product
        ("Heinz Baked Beans 415g", "Heinz Cream of Tomato Soup 400g"),  # Same brand, different product
        ("Heinz Baked Beans 415g", "Tesco Milk 2.272L"),  # Completely different
    ]
    
    for name1, name2 in test_pairs:
        # Test brand similarity
        brand_sim = matcher.check_brand_similarity(name1, name2)
        
        # Test weight similarity
        weight_sim = matcher.check_weight_similarity(name1, name2)
        
        # Test overall matching
        match = matcher.enhanced_product_match(name1, [{'name': name2, 'price': 1.50, 'retailer': 'Test'}])
        
        print(f"Comparing: {name1}")
        print(f"With:      {name2}")
        print(f"Brand similarity: {brand_sim:.2f}")
        print(f"Weight similarity: {weight_sim:.2f}")
        if match:
            print(f"Match confidence: {match.confidence:.2f} ({match.match_type})")
        else:
            print("No match found")
        print()


def test_price_validation():
    """Test price validation functionality"""
    print("🧪 Testing Price Validation")
    print("=" * 40)
    
    matcher = EnhancedProductMatcher()
    
    # Test cases with various price scenarios
    test_cases = [
        {
            'name': 'Heinz Baked Beans 415g',
            'price': 0.85,
            'unit_price': 2.05,
            'weight': 415
        },
        {
            'name': 'Tesco Milk 2.272L',
            'price': 1.25,
            'unit_price': 0.55,
            'weight': 2272
        },
        {
            'name': 'Heinz Baked Beans 415g',
            'price': 5.00,  # Suspiciously high
            'unit_price': 12.05,
            'weight': 415
        },
        {
            'name': 'Bread 800g',
            'price': 0.50,  # Suspiciously low
            'unit_price': 0.63,
            'weight': 800
        },
    ]
    
    for case in test_cases:
        issues = matcher.validate_price_extraction(
            case['name'], case['price'], case['unit_price'], case['weight']
        )
        
        print(f"Product: {case['name']}")
        print(f"Price: £{case['price']:.2f}")
        print(f"Unit Price: £{case['unit_price']:.2f}")
        print(f"Weight: {case['weight']}")
        
        if issues:
            print("⚠️  Validation Issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ No validation issues")
        print()


def test_ml_matcher():
    """Test the machine learning matcher (if available)"""
    print("🧪 Testing ML Matcher")
    print("=" * 40)
    
    try:
        ml_matcher = MLProductMatcher()
        
        # Sample product names for training
        training_products = [
            "Heinz Baked Beans 415g",
            "Heinz Baked Beans 420g",
            "Heinz Cream of Tomato Soup 400g",
            "Tesco Baked Beans 420g",
            "Branston Baked Beans 410g",
            "Tesco Milk 2.272L",
            "Sainsbury's Milk 2.272L",
            "ASDA Milk 2.272L",
        ]
        
        # Train the model
        ml_matcher.train(training_products)
        print(f"✅ Trained on {len(training_products)} products")
        
        # Test matching
        test_queries = [
            "Heinz Baked Beans 415g",
            "Heinz Beanz 415g",
            "Tesco Baked Beans",
            "Milk 2L",
        ]
        
        for query in test_queries:
            match, confidence = ml_matcher.find_best_match(query)
            print(f"Query: {query}")
            if match:
                print(f"Best match: {match}")
                print(f"Confidence: {confidence:.2f}")
            else:
                print("No match found")
            print()
            
    except ImportError as e:
        print(f"❌ ML features not available: {e}")
    except Exception as e:
        print(f"❌ Error testing ML matcher: {e}")


async def test_enhanced_scraper_integration():
    """Test the enhanced scraper integration"""
    print("🧪 Testing Enhanced Scraper Integration")
    print("=" * 50)
    
    try:
        scraper = EnhancedScraper()
        
        # Test with a simple product
        product_name = "Heinz Baked Beans 415g"
        print(f"Testing enhanced scraping for: {product_name}")
        
        results = await scraper.enhanced_scrape_product_prices(product_name)
        
        if results:
            print(f"✅ Found {len(results)} enhanced matches")
            scraper.print_enhanced_results(results)
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Error testing enhanced scraper: {e}")


def run_all_tests():
    """Run all tests"""
    print("🚀 Running Enhanced Product Matching Tests")
    print("=" * 60)
    
    # Run individual tests
    test_text_cleaning()
    test_weight_extraction()
    test_brand_extraction()
    test_similarity_matching()
    test_price_validation()
    test_ml_matcher()
    
    # Run integration test
    print("\n" + "=" * 60)
    asyncio.run(test_enhanced_scraper_integration())
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    run_all_tests()
