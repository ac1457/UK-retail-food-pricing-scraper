#!/usr/bin/env python3
"""
Simple Test for Enhanced Product Matching System
===============================================

A simplified test that demonstrates the enhanced matching functionality
without requiring external dependencies.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SimpleProductMatch:
    """Simple data class for product match results"""
    name: str
    price: Optional[float]
    confidence: float
    match_type: str
    validation_issues: List[str]
    retailer: str


class SimpleEnhancedMatcher:
    """Simplified enhanced product matcher without external dependencies"""
    
    def __init__(self):
        # Common retail phrases to remove
        self.remove_phrases = [
            r'\b\d+\s*[x×]\b',  # Quantity indicators (2x, 3x)
            r'\boffer\b', r'\bdeal\b', r'\bspecial\b',
            r'\bclubcard\b', r'\bprice\b', r'\bwas\b', r'\bnow\b',
            r'\b\d+\s*for\s*£?\d+\.?\d*\b',  # Multi-buy offers
            r'\bsave\b', r'\breduced\b', r'\bclearance\b',
            r'\bnew\b', r'\bimproved\b', r'\bformula\b'
        ]
        
        # Weight/volume patterns
        self.weight_patterns = [
            (r'(\d+)\s*[gG]', 'g'),  # grams
            (r'(\d+)\s*[kK][gG]', 'kg'),  # kilograms
            (r'(\d+)\s*[mM][lL]', 'ml'),  # milliliters
            (r'(\d+)\s*[lL]', 'l'),  # liters
            (r'(\d+)\s*[pP][cC]', 'pc'),  # pieces
            (r'(\d+)\s*pack', 'pack'),  # pack
            (r'(\d+)\s*[xX]', 'x'),  # multiplier
        ]
        
        # Expected price ranges by category
        self.expected_ranges = {
            'milk': (0.50, 2.50),
            'bread': (0.80, 3.00),
            'eggs': (1.00, 4.00),
            'cheese': (1.50, 8.00),
            'baked beans': (0.30, 2.00),
            'soup': (0.50, 3.00),
            'pasta': (0.50, 3.00),
            'rice': (0.50, 4.00),
            'cereal': (1.00, 5.00),
            'yogurt': (0.50, 3.00),
            'butter': (1.00, 4.00),
            'chicken': (2.00, 8.00),
            'beef': (3.00, 12.00),
            'fish': (2.00, 10.00),
            'vegetables': (0.50, 4.00),
            'fruit': (0.50, 5.00),
        }
    
    def clean_product_text(self, text: str) -> str:
        """Standardize product text for better matching"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove common retail phrases
        for phrase in self.remove_phrases:
            text = re.sub(phrase, '', text)
        
        # Remove punctuation and extra spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_weight_volume(self, text: str) -> Tuple[Optional[float], Optional[str]]:
        """Extract weight/volume information for better matching"""
        if not text:
            return None, None
        
        text_lower = text.lower()
        
        for pattern, unit in self.weight_patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = float(match.group(1))
                return value, unit
        
        return None, None
    
    def extract_brand_and_product(self, product_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract brand and product name from product string"""
        if not product_name:
            return None, None
        
        # Common brand patterns
        brand_patterns = [
            r'^(heinz|branston|tesco|sainsbury|asda|morrisons|ocado|co-op|aldi|lidl|waitrose)\b',
            r'^(nestle|kellogg|unilever|kraft|mars|cadbury|walkers|coca-cola|pepsi)\b',
            r'^(dove|lynx|axe|rexona|sure|nivea|garnier|loreal|maybelline)\b',
        ]
        
        product_name_lower = product_name.lower()
        
        for pattern in brand_patterns:
            match = re.search(pattern, product_name_lower)
            if match:
                brand = match.group(1)
                # Remove brand from product name
                product = re.sub(pattern, '', product_name_lower).strip()
                return brand, product
        
        return None, product_name_lower
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using simple word overlap"""
        if not text1 or not text2:
            return 0.0
        
        # Clean both texts
        clean1 = self.clean_product_text(text1)
        clean2 = self.clean_product_text(text2)
        
        # Split into words
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def check_brand_similarity(self, name1: str, name2: str) -> float:
        """Check brand similarity between two product names"""
        brand1, _ = self.extract_brand_and_product(name1)
        brand2, _ = self.extract_brand_and_product(name2)
        
        if not brand1 or not brand2:
            return 0.0
        
        # Exact brand match
        if brand1.lower() == brand2.lower():
            return 1.0
        
        # Simple similarity for brand variations
        if brand1.lower() in brand2.lower() or brand2.lower() in brand1.lower():
            return 0.8
        
        return 0.0
    
    def check_weight_similarity(self, name1: str, name2: str) -> float:
        """Check weight/volume similarity between two product names"""
        weight1, unit1 = self.extract_weight_volume(name1)
        weight2, unit2 = self.extract_weight_volume(name2)
        
        if not weight1 or not weight2:
            return 0.0
        
        # Convert to same unit for comparison (simplified)
        if unit1 == unit2:
            # Same unit, compare directly
            if weight1 == weight2:
                return 1.0
            
            # Allow for some tolerance (within 10%)
            tolerance = 0.1
            if abs(weight1 - weight2) / max(weight1, weight2) <= tolerance:
                return 0.8
        
        return 0.0
    
    def enhanced_product_match(self, product_name: str, scraped_items: List[Dict], 
                             threshold: float = 0.7) -> Optional[SimpleProductMatch]:
        """Match products using multiple criteria"""
        if not scraped_items:
            return None
        
        product_name_clean = self.clean_product_text(product_name)
        best_match = None
        highest_score = 0
        
        for item in scraped_items:
            item_name = item.get('name', '')
            if not item_name:
                continue
            
            item_name_clean = self.clean_product_text(item_name)
            
            # 1. Exact match
            if product_name_clean == item_name_clean:
                return self._create_simple_product_match(item, 1.0, 'exact')
            
            # 2. Similarity matching
            similarity = self.calculate_similarity(product_name, item_name)
            
            # 3. Brand matching
            brand_match = self.check_brand_similarity(product_name, item_name)
            
            # 4. Weight/volume matching
            weight_match = self.check_weight_similarity(product_name, item_name)
            
            # Combined score with weights
            total_score = (similarity * 0.6 + brand_match * 0.2 + weight_match * 0.2)
            
            if total_score > highest_score and total_score > threshold:
                highest_score = total_score
                best_match = item
        
        if best_match:
            return self._create_simple_product_match(best_match, highest_score, 'fuzzy')
        
        return None
    
    def _create_simple_product_match(self, item: Dict, confidence: float, match_type: str) -> SimpleProductMatch:
        """Create a SimpleProductMatch object from scraped item"""
        name = item.get('name', '')
        price = self._extract_price(item)
        
        # Validate the match
        validation_issues = self.validate_price_extraction(name, price)
        
        return SimpleProductMatch(
            name=name,
            price=price,
            confidence=confidence,
            match_type=match_type,
            validation_issues=validation_issues,
            retailer=item.get('retailer', 'Unknown')
        )
    
    def _extract_price(self, item: Dict) -> Optional[float]:
        """Extract price from item data"""
        price_text = item.get('price', '') or item.get('price_text', '')
        if not price_text:
            return None
        
        # Common price patterns
        price_patterns = [
            r'£(\d+\.\d{2})',
            r'£(\d+)',
            r'(\d+\.\d{2})p',
            r'(\d+)p',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, str(price_text))
            if match:
                value = float(match.group(1))
                if 'p' in pattern:
                    value /= 100  # Convert pence to pounds
                return value
        
        return None
    
    def validate_price_extraction(self, product_name: str, price: Optional[float]) -> List[str]:
        """Validate that the scraped price makes sense"""
        validation_issues = []
        
        if not price:
            validation_issues.append("No price found")
            return validation_issues
        
        # Price range validation
        product_name_lower = product_name.lower()
        for category, (min_price, max_price) in self.expected_ranges.items():
            if category in product_name_lower:
                if price < min_price or price > max_price:
                    validation_issues.append(
                        f"Price £{price:.2f} outside expected range £{min_price:.2f}-£{max_price:.2f} for {category}"
                    )
                break
        
        return validation_issues


def test_text_cleaning():
    """Test the text cleaning functionality"""
    print("🧪 Testing Text Cleaning")
    print("=" * 40)
    
    matcher = SimpleEnhancedMatcher()
    
    test_cases = [
        "Heinz Baked Beans 415g 2x Clubcard Price",
        "Tesco Baked Beans 420g Special Offer",
        "Branston Baked Beans 410g 3 for £2",
        "Heinz Cream of Tomato Soup 400g New Formula",
    ]
    
    for text in test_cases:
        cleaned = matcher.clean_product_text(text)
        print(f"Original: {text}")
        print(f"Cleaned:  {cleaned}")
        print()


def test_weight_extraction():
    """Test weight/volume extraction"""
    print("🧪 Testing Weight/Volume Extraction")
    print("=" * 40)
    
    matcher = SimpleEnhancedMatcher()
    
    test_cases = [
        "Heinz Baked Beans 415g",
        "Tesco Milk 2.272L",
        "Branston Pickle 454g",
        "Heinz Soup 400ml",
        "Eggs 6 Pack",
        "Bread 800g",
    ]
    
    for text in test_cases:
        weight, unit = matcher.extract_weight_volume(text)
        print(f"Text: {text}")
        print(f"Weight: {weight}, Unit: {unit}")
        print()


def test_brand_extraction():
    """Test brand and product extraction"""
    print("🧪 Testing Brand Extraction")
    print("=" * 40)
    
    matcher = SimpleEnhancedMatcher()
    
    test_cases = [
        "Heinz Baked Beans 415g",
        "Tesco Baked Beans 420g",
        "Branston Pickle 454g",
        "Sainsbury's Baked Beans 410g",
        "ASDA Milk 2.272L",
    ]
    
    for text in test_cases:
        brand, product = matcher.extract_brand_and_product(text)
        print(f"Text: {text}")
        print(f"Brand: {brand}")
        print(f"Product: {product}")
        print()


def test_similarity_matching():
    """Test similarity matching between products"""
    print("🧪 Testing Similarity Matching")
    print("=" * 40)
    
    matcher = SimpleEnhancedMatcher()
    
    # Test cases with expected high similarity
    test_pairs = [
        ("Heinz Baked Beans 415g", "Heinz Baked Beans 415g"),  # Exact match
        ("Heinz Baked Beans 415g", "Heinz Baked Beans 420g"),  # Same brand, similar weight
        ("Heinz Baked Beans 415g", "Tesco Baked Beans 420g"),  # Different brand, same product
        ("Heinz Baked Beans 415g", "Branston Baked Beans 410g"),  # Different brand, same product
        ("Heinz Baked Beans 415g", "Heinz Cream of Tomato Soup 400g"),  # Same brand, different product
        ("Heinz Baked Beans 415g", "Tesco Milk 2.272L"),  # Completely different
    ]
    
    for name1, name2 in test_pairs:
        # Test brand similarity
        brand_sim = matcher.check_brand_similarity(name1, name2)
        
        # Test weight similarity
        weight_sim = matcher.check_weight_similarity(name1, name2)
        
        # Test overall similarity
        similarity = matcher.calculate_similarity(name1, name2)
        
        print(f"Comparing: {name1}")
        print(f"With:      {name2}")
        print(f"Brand similarity: {brand_sim:.2f}")
        print(f"Weight similarity: {weight_sim:.2f}")
        print(f"Overall similarity: {similarity:.2f}")
        print()


def test_enhanced_matching():
    """Test the enhanced matching system"""
    print("🧪 Testing Enhanced Matching")
    print("=" * 40)
    
    matcher = SimpleEnhancedMatcher()
    
    # Test product to search for
    product_name = "Heinz Baked Beans 415g"
    
    # Sample scraped items
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
        },
        {
            'name': 'Branston Baked Beans 410g',
            'price': 0.80,
            'retailer': 'Sainsbury\'s'
        },
        {
            'name': 'Heinz Cream of Tomato Soup 400g',
            'price': 1.20,
            'retailer': 'ASDA'
        },
        {
            'name': 'Tesco Milk 2.272L',
            'price': 1.25,
            'retailer': 'Tesco'
        }
    ]
    
    print(f"Searching for: {product_name}")
    print(f"Available items: {len(scraped_items)}")
    print()
    
    # Find the best match
    match = matcher.enhanced_product_match(product_name, scraped_items, threshold=0.5)
    
    if match:
        print(f"✅ Best match found!")
        print(f"Product: {match.name}")
        if match.price is not None:
            print(f"Price: £{match.price:.2f}")
        else:
            print(f"Price: N/A")
        print(f"Retailer: {match.retailer}")
        print(f"Confidence: {match.confidence:.2%}")
        print(f"Match type: {match.match_type}")
        
        if match.validation_issues:
            print("⚠️  Validation Issues:")
            for issue in match.validation_issues:
                print(f"   - {issue}")
        else:
            print("✅ No validation issues")
    else:
        print("❌ No match found")


def test_price_validation():
    """Test price validation functionality"""
    print("🧪 Testing Price Validation")
    print("=" * 40)
    
    matcher = SimpleEnhancedMatcher()
    
    # Test cases with various price scenarios
    test_cases = [
        {
            'name': 'Heinz Baked Beans 415g',
            'price': 0.85,
        },
        {
            'name': 'Tesco Milk 2.272L',
            'price': 1.25,
        },
        {
            'name': 'Heinz Baked Beans 415g',
            'price': 5.00,  # Suspiciously high
        },
        {
            'name': 'Bread 800g',
            'price': 0.50,  # Suspiciously low
        },
    ]
    
    for case in test_cases:
        issues = matcher.validate_price_extraction(case['name'], case['price'])
        
        print(f"Product: {case['name']}")
        print(f"Price: £{case['price']:.2f}")
        
        if issues:
            print("⚠️  Validation Issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ No validation issues")
        print()


def run_all_tests():
    """Run all tests"""
    print("🚀 Running Simple Enhanced Product Matching Tests")
    print("=" * 60)
    
    # Run individual tests
    test_text_cleaning()
    test_weight_extraction()
    test_brand_extraction()
    test_similarity_matching()
    test_enhanced_matching()
    test_price_validation()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    run_all_tests()
