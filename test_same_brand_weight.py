#!/usr/bin/env python3
"""
Test Same Brand and Weight Matching
===================================

Demonstrates the new functionality to match products with the same brand
and weight but different flavors.
"""

from enhanced_matcher import EnhancedProductMatcher

def test_same_brand_weight_matching():
    """Test the same brand and weight matching functionality"""
    
    print("🧪 Testing Same Brand and Weight Matching")
    print("=" * 50)
    
    matcher = EnhancedProductMatcher()
    
    # Test cases with same brand and weight but different flavors
    test_cases = [
        {
            'search_product': 'Heinz Tomato Soup 400g',
            'scraped_items': [
                {
                    'name': 'Heinz Cream of Tomato Soup 400g',
                    'price': '£1.70',
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Heinz Chicken Soup 400g',
                    'price': '£1.70',
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Heinz Vegetable Soup 400g',
                    'price': '£1.70',
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Campbell\'s Tomato Soup 400g',
                    'price': '£1.10',
                    'retailer': 'Sainsbury\'s'
                }
            ]
        },
        {
            'search_product': 'Cadbury Dairy Milk Chocolate 100g',
            'scraped_items': [
                {
                    'name': 'Cadbury Dairy Milk Caramel 100g',
                    'price': '£1.50',
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Cadbury Dairy Milk Fruit & Nut 100g',
                    'price': '£1.55',
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Cadbury Dairy Milk Oreo 100g',
                    'price': '£1.60',
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Galaxy Chocolate 100g',
                    'price': '£1.45',
                    'retailer': 'Sainsbury\'s'
                }
            ]
        },
        {
            'search_product': 'Walkers Ready Salted Crisps 150g',
            'scraped_items': [
                {
                    'name': 'Walkers Cheese & Onion Crisps 150g',
                    'price': '£1.80',
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Walkers Salt & Vinegar Crisps 150g',
                    'price': '£1.80',
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Walkers Prawn Cocktail Crisps 150g',
                    'price': '£1.85',
                    'retailer': 'Tesco'
                },
                {
                    'name': 'Pringles Original 150g',
                    'price': '£2.00',
                    'retailer': 'Sainsbury\'s'
                }
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📦 Test Case {i}: {test_case['search_product']}")
        print("-" * 40)
        
        # Run enhanced matching
        match = matcher.enhanced_product_match(
            test_case['search_product'], 
            test_case['scraped_items'], 
            threshold=0.5
        )
        
        if match:
            print(f"✅ Match found!")
            print(f"   Product: {match.name}")
            if match.price is not None:
                print(f"   Price: £{match.price:.2f}")
            else:
                print(f"   Price: N/A")
            print(f"   Retailer: {match.retailer}")
            print(f"   Confidence: {match.confidence:.2%}")
            print(f"   Match Type: {match.match_type}")
            
            if match.validation_issues:
                print(f"   ⚠️  Validation Issues:")
                for issue in match.validation_issues:
                    print(f"      - {issue}")
            else:
                print(f"   ✅ No validation issues")
        else:
            print(f"❌ No match found")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    test_same_brand_weight_matching()
