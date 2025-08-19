#!/usr/bin/env python3
"""
Test Enhanced Workflow
=====================

Test the enhanced price scraping workflow with multi-source aggregation
"""

import sys
import os
from price_aggregator import PriceAggregator


def test_enhanced_workflow():
    """Test the enhanced workflow with sample products"""
    
    print("🧪 TESTING ENHANCED PRICE WORKFLOW")
    print("=" * 50)
    
    # Initialize aggregator with Tesco enabled
    aggregator = PriceAggregator(enable_tesco=True)
    
    # Test products (including the problematic ones)
    test_products = [
        "Heinz Beanz 6 x 415g",
        "Branston Baked Beans 4 x 410g", 
        "Heinz Cream of Tomato Soup 4 x 400g",
        "Alfez Moroccan Cous Cous 200g",
        "Daddies Brown Sauce 285g"
    ]
    
    results = []
    
    for i, product in enumerate(test_products, 1):
        print(f"\n🔍 Test {i}/5: {product}")
        print("-" * 40)
        
        try:
            # Get best prices
            result = aggregator.get_best_prices(product)
            
            if result['found']:
                best_match = result['best_match']
                print(f"✅ FOUND: {best_match['name']}")
                print(f"   Source: {best_match['source']}")
                print(f"   Price: £{best_match['price']}")
                print(f"   Confidence: {result['confidence']:.3f}")
                print(f"   Similarity: {best_match['similarity']:.3f}")
                
                # Show retailer breakdown if available
                if best_match['source'] == 'Trolley.co.uk':
                    retailer_prices = best_match['retailer_prices']
                    print(f"   Retailer Prices:")
                    for retailer, price_data in retailer_prices.items():
                        if isinstance(price_data, dict) and 'price' in price_data:
                            print(f"     {retailer}: £{price_data['price']}")
                
                results.append({
                    'product': product,
                    'found': True,
                    'confidence': result['confidence'],
                    'source': best_match['source']
                })
            else:
                print(f"❌ NOT FOUND")
                results.append({
                    'product': product,
                    'found': False,
                    'confidence': 0.0,
                    'source': 'None'
                })
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                'product': product,
                'found': False,
                'confidence': 0.0,
                'source': 'Error'
            })
    
    # Print summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 50)
    
    found_count = sum(1 for r in results if r['found'])
    total_count = len(results)
    
    print(f"Total Products: {total_count}")
    print(f"Found: {found_count} ({found_count/total_count*100:.1f}%)")
    print(f"Not Found: {total_count - found_count}")
    
    print(f"\nDetailed Results:")
    for result in results:
        status = "✅" if result['found'] else "❌"
        print(f"{status} {result['product']}")
        if result['found']:
            print(f"   Source: {result['source']}, Confidence: {result['confidence']:.3f}")
    
    # Check for specific issues
    print(f"\n🔍 SPECIFIC CHECKS:")
    
    # Check Heinz Beanz multipack
    heinz_result = next((r for r in results if "Heinz Beanz" in r['product']), None)
    if heinz_result and heinz_result['found']:
        print(f"✅ Heinz Beanz multipack found successfully")
    else:
        print(f"❌ Heinz Beanz multipack not found")
    
    # Check Branston multipack
    branston_result = next((r for r in results if "Branston" in r['product']), None)
    if branston_result and branston_result['found']:
        print(f"✅ Branston multipack found successfully")
    else:
        print(f"❌ Branston multipack not found")
    
    print(f"\n🎯 ENHANCED WORKFLOW TEST COMPLETED")


if __name__ == "__main__":
    test_enhanced_workflow()
