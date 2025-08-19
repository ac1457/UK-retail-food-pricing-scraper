#!/usr/bin/env python3
"""
Test workflow with cache cleared to verify Heinz fix
"""

import sys
import os
import pandas as pd

# Add scraper directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.final_fixed_workflow import FinalFixedWorkflow

def test_workflow_heinz():
    """Test the workflow with Heinz multipack"""
    print("🧪 Testing workflow with cache cleared")
    print("=" * 50)
    
    # Initialize workflow with cache cleared
    workflow = FinalFixedWorkflow(clear_cache=True)
    
    # Create a test DataFrame with just the Heinz product
    test_data = pd.DataFrame({
        'Product_Name': ['Heinz Beanz 6 x 415g']
    })
    
    print("📝 Test data:")
    print(test_data)
    
    # Process the test data
    print("\n🔍 Processing test data...")
    
    # Save test data to temporary file
    test_file = "test_heinz_data.xlsx"
    test_data.to_excel(test_file, index=False)
    
    try:
        # Process the file
        results = workflow.process_excel_file(test_file, "test_heinz_results.xlsx")
        
        print("\n📊 Results:")
        print(results)
        
        # Check if we got the correct URL
        if not results.empty:
            url = results.iloc[0].get('Trolley_URL', '')
            if 'heinz-beanz-family-pack' in url:
                print("\n✅ SUCCESS: Found correct Heinz Family Pack URL!")
            else:
                print(f"\n❌ FAILED: Got wrong URL: {url}")
                print("Expected: https://www.trolley.co.uk/product/heinz-beanz-family-pack/DJC713")
        
    finally:
        # Clean up test files
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists("test_heinz_results.xlsx"):
            os.remove("test_heinz_results.xlsx")

if __name__ == "__main__":
    test_workflow_heinz()
