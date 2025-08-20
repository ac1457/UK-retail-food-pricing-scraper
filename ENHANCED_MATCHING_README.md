# Enhanced Product Matching System

## Overview

The Enhanced Product Matching System provides advanced product matching capabilities for the UK retail food pricing scraper. It implements multiple strategies for accurate product identification, validation, and price extraction across different retailers.

## Features

### 1. Enhanced Product Matching
- **Multiple Identifiers**: Uses brand, product type, weight/volume, and fuzzy matching
- **Fuzzy Matching**: Implements token-based similarity with configurable thresholds
- **Brand Recognition**: Identifies and matches product brands across retailers
- **Weight/Volume Extraction**: Extracts and compares product weights for better matching

### 2. Improved Text Cleaning
- **Retail Phrase Removal**: Removes common retail phrases like "Clubcard Price", "Special Offer"
- **Standardization**: Normalizes product names for consistent comparison
- **Punctuation Handling**: Cleans and standardizes text formatting

### 3. Store-Specific Parsing
- **Retailer Configurations**: Custom parsing rules for Tesco, Sainsbury's, ASDA, etc.
- **Price Extraction**: Retailer-specific price pattern recognition
- **Unit Price Calculation**: Automatic unit price extraction and validation

### 4. Enhanced Validation
- **Price Range Validation**: Checks prices against expected ranges by product category
- **Unit Price Sanity Checks**: Validates unit price calculations
- **Weight Validation**: Flags unusually large or small weights
- **Comprehensive Reporting**: Detailed validation issue reporting

### 5. Machine Learning Approach (Optional)
- **TF-IDF Vectorization**: Text-based similarity using scikit-learn
- **Cosine Similarity**: Advanced matching for complex product names
- **Training Capabilities**: Can be trained on known product datasets

## Installation

### Prerequisites
```bash
pip install -r requirements.txt
```

### Dependencies
- `fuzzywuzzy>=0.18.0` - Fuzzy string matching
- `python-Levenshtein>=0.21.0` - Fast string similarity
- `numpy>=1.24.0` - Numerical operations
- `scikit-learn>=1.3.0` - Machine learning features (optional)

## Usage

### Basic Usage

```python
from enhanced_matcher import EnhancedProductMatcher

# Initialize the matcher
matcher = EnhancedProductMatcher()

# Match a product against scraped items
product_name = "Heinz Baked Beans 415g"
scraped_items = [
    {
        'name': 'Heinz Baked Beans 415g Clubcard Price',
        'price': 0.85,
        'retailer': 'Tesco'
    },
    {
        'name': 'Tesco Baked Beans 420g',
        'price': 0.75,
        'retailer': 'Tesco'
    }
]

# Find the best match
match = matcher.enhanced_product_match(product_name, scraped_items)

if match:
    print(f"Best match: {match.name}")
    print(f"Price: £{match.price}")
    print(f"Confidence: {match.confidence:.2%}")
    print(f"Match type: {match.match_type}")
    
    if match.validation_issues:
        print("Validation issues:")
        for issue in match.validation_issues:
            print(f"  - {issue}")
```

### Enhanced Scraper Integration

```python
from enhanced_scraper import EnhancedScraper
import asyncio

async def main():
    # Initialize enhanced scraper
    scraper = EnhancedScraper()
    
    # Search for products with enhanced matching
    results = await scraper.enhanced_scrape_product_prices("Heinz Baked Beans 415g")
    
    # Print results with validation
    scraper.print_enhanced_results(results)

# Run the scraper
asyncio.run(main())
```

### Machine Learning Matcher

```python
from enhanced_matcher import MLProductMatcher

# Initialize ML matcher
ml_matcher = MLProductMatcher()

# Train on known products
training_products = [
    "Heinz Baked Beans 415g",
    "Heinz Baked Beans 420g",
    "Tesco Baked Beans 420g",
    "Branston Baked Beans 410g"
]

ml_matcher.train(training_products)

# Find matches
match, confidence = ml_matcher.find_best_match("Heinz Beanz 415g")
if match:
    print(f"ML Match: {match} (confidence: {confidence:.2f})")
```

## Configuration

### Retailer Configuration

The system includes pre-configured settings for major UK retailers:

```python
RETAILER_CONFIG = {
    'tesco': {
        'selectors': {
            'product': '[data-auto="product-tile"]',
            'name': 'h3',
            'price': '[data-auto="price-value"]',
            'unit_price': '[data-auto="price-per-quantity-weight"]'
        },
        'parser': parse_tesco_product
    },
    'sainsburys': {
        'selectors': {
            'product': '.gridItem',
            'name': '.productName',
            'price': '.pricePerUnit',
        },
        'parser': parse_sainsburys_product
    }
}
```

### Price Range Validation

Configure expected price ranges by product category:

```python
expected_ranges = {
    'milk': (0.50, 2.50),
    'bread': (0.80, 3.00),
    'eggs': (1.00, 4.00),
    'cheese': (1.50, 8.00),
    'baked beans': (0.30, 2.00),
    # Add more categories as needed
}
```

## Testing

Run the comprehensive test suite:

```bash
python test_enhanced_matching.py
```

The test suite covers:
- Text cleaning functionality
- Weight/volume extraction
- Brand extraction
- Similarity matching
- Price validation
- ML matcher (if available)
- Integration testing

## Advanced Features

### Custom Weight Patterns

Add custom weight/volume patterns:

```python
matcher = EnhancedProductMatcher()
matcher.weight_patterns.append((r'(\d+)\s*[bB][oO][tT]', 'bot'))  # Bottles
```

### Custom Brand Patterns

Extend brand recognition:

```python
# Add to brand_patterns in extract_brand_and_product method
brand_patterns.append(r'^(your-brand|another-brand)\b')
```

### Custom Validation Rules

Add product-specific validation:

```python
def custom_validation(product_name, price, unit_price, weight):
    # Add your custom validation logic
    issues = []
    
    # Example: Check for premium products
    if 'premium' in product_name.lower() and price < 2.00:
        issues.append("Premium product price seems too low")
    
    return issues
```

## Performance Considerations

### Caching
- The system integrates with the existing cache manager
- Results are cached to avoid re-scraping
- Cache duration is configurable

### Optimization
- Fuzzy matching uses optimized algorithms
- ML features are optional and only loaded when needed
- Batch processing for multiple products

### Memory Usage
- TF-IDF vectors are stored in memory for ML matching
- Consider clearing vectors for large datasets
- Use streaming for very large product catalogs

## Troubleshooting

### Common Issues

1. **Low Match Confidence**
   - Check product name formatting
   - Verify brand extraction
   - Adjust similarity thresholds

2. **Validation Errors**
   - Review price range configurations
   - Check weight/volume extraction
   - Verify unit price calculations

3. **ML Matcher Not Working**
   - Ensure scikit-learn is installed
   - Check training data quality
   - Verify vectorizer configuration

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

matcher = EnhancedProductMatcher()
# Debug information will be printed
```

## Contributing

### Adding New Retailers

1. Create a parsing function:
```python
def parse_new_retailer_product(item: Dict) -> Dict:
    # Implement retailer-specific parsing
    return {
        'name': cleaned_name,
        'price': extracted_price,
        'unit_price': extracted_unit_price,
        'weight': extracted_weight,
        'retailer': 'New Retailer'
    }
```

2. Add to configuration:
```python
RETAILER_CONFIG['new_retailer'] = {
    'selectors': {...},
    'parser': parse_new_retailer_product
}
```

### Extending Validation

Add new validation rules to the `validate_price_extraction` method:

```python
def validate_price_extraction(self, product_name, price, unit_price, weight):
    issues = []
    
    # Add your custom validation logic here
    
    return issues
```

## License

This enhanced matching system is part of the UK retail food pricing scraper project and follows the same licensing terms.

## Support

For issues and questions:
1. Check the test suite for examples
2. Review the configuration options
3. Enable debug logging for detailed information
4. Consult the main scraper documentation
