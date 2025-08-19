#!/usr/bin/env python3
"""
Test workflow multipack handling
"""

from main import FinalFixedWorkflow

def test_workflow_multipack():
    """Test workflow multipack handling"""
    print("🧪 Testing Workflow Multipack Handling")
    print("=" * 50)
    
    # Initialize workflow with clear cache
    workflow = FinalFixedWorkflow(clear_cache=True)
    
    # Test the problematic product
    product = "Heinz Beanz 6 x 415g"
    print(f"🔍 Testing: {product}")
    
    # Test the scraper directly
    trolley_results = workflow.scraper.search_product(product)
    
    if trolley_results:
        print(f"✅ Found {len(trolley_results)} results")
        for i, result in enumerate(trolley_results[:5], 1):
            print(f"  {i}. {result['name']} (Score: {result['similarity_score']:.3f})")
            print(f"     URL: {result['url']}")
            print(f"     Is multipack: {workflow.scraper._is_multipack(result['name'])}")
        
        best = max(trolley_results, key=lambda x: x['similarity_score'])
        print(f"\n🏆 Best match: {best['name']} (Score: {best['similarity_score']:.3f})")
        print(f"   URL: {best['url']}")
        print(f"   Is multipack: {workflow.scraper._is_multipack(best['name'])}")
        
        # Check if it's the correct product
        if "baked beans" in best['name'].lower() and "family pack" in best['name'].lower():
            print("✅ SUCCESS: Correctly matched Heinz Baked Beans Family Pack!")
        else:
            print("❌ ERROR: Still matching wrong product!")
    else:
        print("❌ No results found")

if __name__ == "__main__":
    test_workflow_multipack()
