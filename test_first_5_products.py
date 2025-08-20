#!/usr/bin/env python3
"""
Test First 5 Products from Excel
================================

Runs the enhanced workflow on the first 5 products from Pricing_Exp.xlsx
to test the system before running on all products.
"""

import pandas as pd
from run_bulk_enhanced_workflow import run_enhanced_workflow_no_cache

def test_first_5_products():
    """Test the enhanced workflow on first 5 products from Excel"""
    
    print("🧪 Testing Enhanced Workflow on First 5 Products")
    print("=" * 60)
    
    # Read products from Excel
    try:
        df = pd.read_excel("Pricing Exp.xlsx")
        
        # Get product names from the Product_Name column
        if 'Product_Name' in df.columns:
            product_names = df['Product_Name'].dropna().tolist()
        else:
            # If column name is different, try to find it
            possible_columns = ['Product Name', 'Product', 'Name', 'Description']
            product_names = []
            for col in possible_columns:
                if col in df.columns:
                    product_names = df[col].dropna().tolist()
                    break
            
            if not product_names:
                # If no matching column found, use the first column
                product_names = df.iloc[:, 0].dropna().tolist()
        
        print(f"📋 Loaded {len(product_names)} products from Excel file")
        
        # Take first 5 products
        first_5_products = product_names[:5]
        
        print(f"\n🎯 Testing first 5 products:")
        for i, product in enumerate(first_5_products, 1):
            print(f"   {i}. {product}")
        
        print(f"\n{'='*60}")
        
        # Process each product
        all_results = []
        successful_matches = 0
        failed_matches = 0
        
        for i, product_name in enumerate(first_5_products, 1):
            print(f"\n📦 Processing {i}/5: {product_name}")
            print(f"{'='*60}")
            
            # Run enhanced workflow for this product
            matches = run_enhanced_workflow_no_cache(product_name)
            
            if matches:
                all_results.extend(matches)
                successful_matches += 1
                print(f"✅ Successfully processed: {product_name}")
            else:
                failed_matches += 1
                print(f"❌ No matches found: {product_name}")
        
        # Print summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY (First 5 Products)")
        print(f"{'='*60}")
        print(f"Total Products Tested: {len(first_5_products)}")
        print(f"Successful Matches: {successful_matches}")
        print(f"Failed Matches: {failed_matches}")
        print(f"Success Rate: {(successful_matches/len(first_5_products)*100):.1f}%")
        print(f"Total Enhanced Matches Found: {len(all_results)}")
        
        # Save results to CSV
        if all_results:
            try:
                df_results = pd.DataFrame(all_results)
                output_file = "test_first_5_results.csv"
                df_results.to_csv(output_file, index=False)
                print(f"\n💾 Results saved to: {output_file}")
                
                # Show sample of results
                print(f"\n📋 Results Summary:")
                print(df_results[['product_name', 'retailer', 'product', 'price', 'confidence', 'match_type']].to_string(index=False))
                
            except Exception as e:
                print(f"❌ Error saving results: {e}")
        
        print(f"\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")

if __name__ == "__main__":
    test_first_5_products()
