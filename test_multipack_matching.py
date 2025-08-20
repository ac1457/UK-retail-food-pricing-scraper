#!/usr/bin/env python3
"""
Test Multipack Weight Matching
===============================

Demonstrates the functionality to match products with different packaging
but the same total weight (e.g., 6 x 25g vs 150g).
"""

from enhanced_matcher import EnhancedProductMatcher

def test_multipack_weight_matching():
    """Test the multipack weight matching functionality"""
    
    print("🧪 Testing Multipack Weight Matching")
    print("=" * 50)
    
    matcher = EnhancedProductMatcher()
    
    # Test weight extraction for different formats
    test_extractions = [
        "Walkers Ready Salted Crisps 6 x 25g",
        "Walkers Ready Salted Crisps 150g", 
        "Coca Cola 4 x 330ml",
        "Coca Cola 1.32l",
        "Heinz Baked Beans 4 x 415g",
        "Heinz Baked Beans 1.66kg",
        "Yogurt 8 x 125g",
        "Yogurt 1kg"
    ]
    
    print("🔍 Weight Extraction Tests:")
    print("-" * 30)
    
    for product in test_extractions:
        weight, unit = matcher.extract_weight_volume(product)
        if weight:
            print(f"{product:35} → {weight}{unit}")
        else:
            print(f"{product:35} → No weight found")
    
    print("\n" + "=" * 50)
    
    # Test cases with multipack vs single pack matching
    test_cases = [
        {
            'search_product': 'Walkers Ready Salted Crisps 6 x 25g',
            'scraped_items': [
                {
                    'name': 'Walkers Ready Salted Crisps 150g',
                    'price': 1.80,
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Walkers Cheese & Onion Crisps 150g',
                    'price': 1.80,
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Pringles Original 200g',
                    'price': 2.50,
                    'retailer': 'Tesco'
                }
            ]
        },
        {
            'search_product': 'Coca Cola 4 x 330ml',
            'scraped_items': [
                {
                    'name': 'Coca Cola 1.32l',
                    'price': 3.50,
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Pepsi 1.5l',
                    'price': 3.25,
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Coca Cola 500ml',
                    'price': 1.25,
                    'retailer': 'Tesco'
                }
            ]
        },
        {
            'search_product': 'Heinz Baked Beans 4 x 415g',
            'scraped_items': [
                {
                    'name': 'Heinz Baked Beans 1.66kg',
                    'price': 4.50,
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Branston Baked Beans 1.5kg',
                    'price': 4.20,
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Heinz Baked Beans 415g',
                    'price': 1.40,
                    'retailer': 'Tesco'
                }
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📦 Test Case {i}: {test_case['search_product']}")
        print("-" * 60)
        
        # Show what weight we extracted from the search product
        search_weight, search_unit = matcher.extract_weight_volume(test_case['search_product'])
        print(f"   Search product weight: {search_weight}{search_unit}")
        
        # Show weights extracted from scraped items
        print(f"   Available products:")
        for j, item in enumerate(test_case['scraped_items'], 1):
            item_weight, item_unit = matcher.extract_weight_volume(item['name'])
            weight_match = matcher.check_weight_similarity(test_case['search_product'], item['name'])
            weight_str = f"{item_weight}{item_unit}" if item_weight else "No weight"
            match_str = f"(Weight match: {weight_match:.2f})"
            print(f"      {j}. {item['name']} → {weight_str} {match_str}")
        
        # Run enhanced matching
        match = matcher.enhanced_product_match(
            test_case['search_product'], 
            test_case['scraped_items'], 
            threshold=0.5
        )
        
        print(f"\n   📋 Enhanced Matching Result:")
        if match:
            print(f"   ✅ Match found!")
            print(f"      Product: {match.name}")
            if match.price is not None:
                print(f"      Price: £{match.price:.2f}")
            else:
                print(f"      Price: N/A")
            print(f"      Retailer: {match.retailer}")
            print(f"      Confidence: {match.confidence:.2%}")
            print(f"      Match Type: {match.match_type}")
            
            if match.validation_issues:
                print(f"      ⚠️  Validation Issues:")
                for issue in match.validation_issues:
                    print(f"         - {issue}")
            else:
                print(f"      ✅ No validation issues")
        else:
            print(f"   ❌ No match found")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_multipack_weight_matching()
