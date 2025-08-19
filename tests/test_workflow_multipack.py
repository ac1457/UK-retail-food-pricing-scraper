#!/usr/bin/env python3
"""
Test Final Workflow with Multipack Fix
=====================================
Test that the final workflow correctly handles multipack products
"""

import sys
import os
import pandas as pd
import tempfile

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from final_fixed_workflow import FinalFixedWorkflow


def test_workflow_multipack_handling():
    """Test that the workflow correctly handles multipack products"""
    print("🧪 Testing Final Workflow Multipack Handling")
    print("=" * 60)
    
    # Create a test Excel file with multipack products
    test_data = {
        'Product_Name': [
            "Heinz Beanz 6 x 415g",
            "Coca Cola 6 x 330ml", 
            "Walkers Crisps 6 Pack",
            "Heinz Beanz 415g",  # Single product for comparison
            "Coca Cola 330ml",   # Single product for comparison
        ]
    }
    
    # Create temporary Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        test_df = pd.DataFrame(test_data)
        test_df.to_excel(tmp_file.name, index=False)
        test_file = tmp_file.name
    
    try:
        print(f"📄 Created test file: {test_file}")
        print(f"📦 Test products:")
        for i, product in enumerate(test_data['Product_Name'], 1):
            print(f"   {i}. {product}")
        
        # Initialize workflow with cache disabled for testing
        workflow = FinalFixedWorkflow(cache_duration_hours=1, clear_cache=True)
        
        # Process the test file
        print(f"\n🔄 Processing test file...")
        results_df = workflow.process_excel_file(
            input_file=test_file,
            output_file=None,  # Don't save output for test
            max_products=5
        )
        
        # Analyze results
        print(f"\n📊 Results Analysis:")
        print("-" * 40)
        
        for index, row in results_df.iterrows():
            product_name = row['Product_Name']
            similarity_score = row['Similarity_Score']
            competitor_price = row['Competitor_Price']
            url = row['URL_Fetched_From']
            
            print(f"\nProduct: {product_name}")
            print(f"  Similarity Score: {similarity_score:.3f}")
            print(f"  Competitor Price: £{competitor_price:.2f}")
            print(f"  URL: {url[:80]}{'...' if len(url) > 80 else ''}")
            
            # Check if it's a multipack
            is_multipack = any(pattern in product_name.lower() for pattern in ['6 x', '4 x', '8 x', '12 x', '6 pack', '4 pack'])
            
            if is_multipack:
                print(f"  📦 MULTIPACK DETECTED")
                if similarity_score >= 0.25:
                    print(f"  ✅ CORRECT: Multipack matched successfully")
                else:
                    print(f"  ❌ ERROR: Multipack not matched (score too low)")
            else:
                print(f"  📦 SINGLE PRODUCT")
                if similarity_score >= 0.25:
                    print(f"  ✅ CORRECT: Single product matched successfully")
                else:
                    print(f"  ❌ ERROR: Single product not matched (score too low)")
        
        # Generate summary
        report = workflow.generate_summary_report(results_df)
        print(f"\n📈 Summary:")
        print(f"  Total products: {report['total_products']}")
        print(f"  Products with matches: {report['products_with_matches']} ({report['match_rate']:.1f}%)")
        print(f"  Products with prices: {report['products_with_prices']} ({report['price_rate']:.1f}%)")
        print(f"  Average similarity: {report['average_similarity']:.3f}")
        
        # Test specific multipack functionality
        print(f"\n🔍 Testing Multipack Logic:")
        scraper = workflow.scraper
        
        # Test the specific Heinz case
        heinz_multipack = "Heinz Beanz 6 x 415g"
        heinz_single = "Heinz Beanz 415g"
        
        quantity1, pack_size1 = scraper._extract_quantity_and_pack_size(heinz_multipack)
        quantity2, pack_size2 = scraper._extract_quantity_and_pack_size(heinz_single)
        
        print(f"  Heinz Multipack: Quantity={quantity1}, Pack size={pack_size1}")
        print(f"  Heinz Single: Quantity={quantity2}, Pack size={pack_size2}")
        
        # Test similarity calculation
        similarity = scraper._calculate_similarity_improved(heinz_multipack, heinz_single)
        quantity_bonus = scraper._calculate_quantity_similarity(heinz_multipack, heinz_single)
        
        print(f"  Similarity between multipack and single: {similarity:.3f}")
        print(f"  Quantity bonus: {quantity_bonus:.3f}")
        
        if quantity_bonus < 0:
            print(f"  ✅ CORRECT: Multipack correctly penalized for pack size mismatch")
        else:
            print(f"  ❌ ERROR: Multipack not penalized for pack size mismatch")
        
        print(f"\n✅ Workflow multipack test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(test_file)
            print(f"🧹 Cleaned up test file")
        except:
            pass


if __name__ == "__main__":
    test_workflow_multipack_handling()
