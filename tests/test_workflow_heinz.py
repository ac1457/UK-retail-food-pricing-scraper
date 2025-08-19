#!/usr/bin/env python3
"""
Test to verify the workflow is using the fixed scraper
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.final_fixed_workflow import FinalFixedWorkflow

def test_workflow_heinz():
    """Test the workflow with Heinz multipack"""
    print("🧪 Testing workflow with Heinz multipack")
    print("=" * 50)
    
    # Initialize workflow with cache cleared
    workflow = FinalFixedWorkflow(clear_cache=True)
    
    # Test the Heinz product directly
    product_name = "Heinz Beanz 6 x 415g"
    print(f"🔍 Testing product: {product_name}")
    
    # Use the scraper directly to see what's happening
    scraper = workflow.scraper
    
    # Test search
    results = scraper.search_product(product_name)
    
    print(f"\n📊 Search Results ({len(results)} found):")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['name']}")
        print(f"   URL: {result['url']}")
        print(f"   Similarity: {result['similarity_score']:.3f}")
        print(f"   Prices: {result['retailer_prices']}")
        
        # Check if this is the correct product
        if "heinz-beanz-family-pack" in result['url']:
            print(f"   ✅ CORRECT PRODUCT FOUND!")
        else:
            print(f"   ❌ Wrong product")
    
    # Check if correct URL was found
    correct_found = any("heinz-beanz-family-pack" in result['url'] for result in results)
    
    if correct_found:
        print(f"\n🎉 SUCCESS: Correct Heinz Family Pack found!")
    else:
        print(f"\n❌ FAILURE: Correct Heinz Family Pack NOT found")
        print(f"Expected URL: https://www.trolley.co.uk/product/heinz-beanz-family-pack/DJC713")

if __name__ == "__main__":
    test_workflow_heinz()
