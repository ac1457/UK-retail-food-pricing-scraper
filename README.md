# Price Comparison Scraper

A comprehensive web scraping tool for price comparison across multiple UK retailers including Trolley.co.uk, Tesco, Morrisons, Ocado, Sainsbury's, Wilko, and Co-op.

## Features

- **Multi-Source Scraping**: Aggregates prices from multiple retailers
- **Smart Product Matching**: Advanced similarity algorithms for accurate product matching
- **Caching System**: File-based caching to improve performance and enable resume capabilities
- **Multipack Support**: Specialized handling for multipack products
- **Configurable Settings**: Easy configuration through settings.ini
- **Batch Processing**: Process large product lists efficiently
- **Priority-Based Results**: Returns prices based on retailer priority (Tesco → Morrisons → Ocado → Sainsbury's → Wilko → Co-op)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd scraper
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with an Excel file containing product data:

```bash
python main.py "your_products.xlsx"
```

### Command Line Options

- `--clear-cache`: Clear all cached data before running
- `--max-products N`: Limit processing to N products (for testing)
- `--enable-tesco`: Enable Tesco scraping
- `--enable-morrisons`: Enable Morrisons scraping
- `--enable-ocado`: Enable Ocado scraping
- `--enable-sainsburys`: Enable Sainsbury's scraping

### Example

```bash
python main.py "Pricing Exp.xlsx" --clear-cache --max-products 10
```

## Input Format

Your Excel file should contain:
- **Product Name**: The name of the product to search for
- **SKU/Barcode**: Product identifier (optional)
- **Quantity**: Product quantity (optional)

## Output

The scraper generates an enhanced Excel file with:
- **Found**: Whether the product was found (Yes/No)
- **Confidence_Level**: High/Medium/Low confidence in the match
- **Confidence_Score**: Numerical confidence score (0-1)
- **Best_Source**: Which retailer provided the best price
- **Matched_Product**: The actual product name found
- **Best_Price**: The best price found
- **Product_URL**: Direct link to the product
- **Similarity_Score**: How similar the match is to the original
- **Individual retailer prices**: Tesco, Morrisons, Ocado, Sainsbury's, Wilko, Co-op

## Configuration

Edit `settings.ini` to customize:
- Request delays and timeouts
- Speed optimization parameters
- Product name mappings

## Project Structure

```
scraper/
├── main.py                 # Main workflow script
├── trolley_scraper_fixed.py # Core Trolley.co.uk scraper
├── tesco_scraper.py        # Tesco direct scraper
├── price_aggregator.py     # Multi-source price aggregation
├── cache_manager.py        # File-based caching system
├── filemanager.py          # File and configuration management
├── settings.ini           # Configuration file
├── constants.py           # Constants and configurations
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Dependencies

- `curl_cffi`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `pandas`: Data manipulation
- `openpyxl`: Excel file handling
- `pathlib`: File path management

## Performance

- **Caching**: Results are cached to avoid redundant requests
- **Batch Processing**: Processes products in batches for efficiency
- **Early Exit**: Stops searching when high-confidence matches are found
- **Smart Delays**: Configurable delays to avoid rate limiting

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure all dependencies are installed
2. **Cache Issues**: Use `--clear-cache` to reset cached data
3. **Rate Limiting**: Increase delays in `settings.ini`
4. **No Results**: Check product names and try different search terms

### Debug Mode

For debugging specific products, create test scripts:

```python
from trolley_scraper_fixed import FixedTrolleyScraper

scraper = FixedTrolleyScraper()
result = scraper.search_with_fallback("Product Name")
print(result)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes. Please respect website terms of service and robots.txt files. Use responsibly and consider implementing appropriate delays between requests.
