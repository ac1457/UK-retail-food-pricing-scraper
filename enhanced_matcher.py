#!/usr/bin/env python3
"""
Enhanced Product Matcher
========================

Advanced product matching system with multiple strategies:
1. Fuzzy matching with multiple algorithms
2. Brand and product type matching
3. Weight/volume extraction and matching
4. Store-specific parsing rules
5. Price validation
6. Machine learning approach (optional)
"""

import re
import string
from typing import Dict, List, Optional, Tuple, Any
from fuzzywuzzy import fuzz, process
import numpy as np
from dataclasses import dataclass
import logging

# Optional ML imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("scikit-learn not available. ML features disabled.")


@dataclass
class ProductMatch:
    """Data class for product match results"""
    name: str
    price: Optional[float]
    unit_price: Optional[float]
    weight: Optional[float]
    confidence: float
    match_type: str
    validation_issues: List[str]
    retailer: str
    url: Optional[str] = None


class EnhancedProductMatcher:
    """Enhanced product matching with multiple strategies"""
    
    def __init__(self):
        self.vectorizer = None
        self.product_vectors = None
        self.product_names = []
        
        # Common retail phrases to remove
        self.remove_phrases = [
            r'\b\d+\s*[x×]\b',  # Quantity indicators (2x, 3x)
            r'\boffer\b', r'\bdeal\b', r'\bspecial\b',
            r'\bclubcard\b', r'\bprice\b', r'\bwas\b', r'\bnow\b',
            r'\b\d+\s*for\s*£?\d+\.?\d*\b',  # Multi-buy offers
            r'\bsave\b', r'\breduced\b', r'\bclearance\b',
            r'\bnew\b', r'\bimproved\b', r'\bformula\b'
        ]
        
        # Phrases that indicate promotional/discounted prices (to be avoided)
        self.promotional_phrases = [
            r'\bclubcard\b', r'\bprice\b', r'\bwas\b', r'\bnow\b',
            r'\boffer\b', r'\bdeal\b', r'\bspecial\b', r'\bsave\b',
            r'\breduced\b', r'\bclearance\b', r'\bmultibuy\b',
            r'\b\d+\s*for\s*£?\d+\.?\d*\b',  # Multi-buy offers
            r'\b\d+\s*[x×]\b',  # Quantity indicators (2x, 3x)
        ]
        
        # Weight/volume patterns
        self.weight_patterns = [
            (r'(\d+(?:\.\d+)?)\s*[gG]', 'g'),  # grams
            (r'(\d+(?:\.\d+)?)\s*[kK][gG]', 'kg'),  # kilograms
            (r'(\d+(?:\.\d+)?)\s*[mM][lL]', 'ml'),  # milliliters
            (r'(\d+(?:\.\d+)?)\s*[lL]', 'l'),  # liters
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
            'baked beans': (0.30, 3.00),
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
    
    def is_promotional_price(self, text: str) -> bool:
        """Check if the product name indicates a promotional/discounted price"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        for phrase in self.promotional_phrases:
            if re.search(phrase, text_lower):
                return True
        
        return False
    
    def extract_weight_volume(self, text: str) -> Tuple[Optional[float], Optional[str]]:
        """Extract weight/volume information for better matching, handling multipacks"""
        if not text:
            return None, None
        
        text_lower = text.lower()
        
        # First, check for multipack formats like "6 x 25g", "4 x 400ml", etc.
        multipack_patterns = [
            (r'(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*([gG])', 'g'),  # 6 x 25g
            (r'(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*([kK][gG])', 'kg'),  # 2 x 1kg
            (r'(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*([mM][lL])', 'ml'),  # 4 x 250ml
            (r'(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*([lL])', 'l'),  # 2 x 1l
        ]
        
        for pattern, unit in multipack_patterns:
            match = re.search(pattern, text_lower)
            if match:
                quantity = float(match.group(1))
                individual_weight = float(match.group(2))
                total_weight = quantity * individual_weight
                return total_weight, unit
        
        # If no multipack found, check for regular weight patterns
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
    
    def check_brand_similarity(self, name1: str, name2: str) -> float:
        """Check brand similarity between two product names"""
        brand1, _ = self.extract_brand_and_product(name1)
        brand2, _ = self.extract_brand_and_product(name2)
        
        if not brand1 or not brand2:
            return 0.0
        
        # Exact brand match
        if brand1.lower() == brand2.lower():
            return 1.0
        
        # Fuzzy brand matching
        similarity = fuzz.ratio(brand1.lower(), brand2.lower()) / 100.0
        
        # Common brand variations
        brand_variations = {
            'heinz': ['heinz'],
            'branston': ['branston'],
            'tesco': ['tesco'],
            'sainsbury': ['sainsbury', 'sainsburys'],
            'asda': ['asda'],
            'morrisons': ['morrisons'],
            'ocado': ['ocado'],
        }
        
        for brand, variations in brand_variations.items():
            if brand1.lower() in variations and brand2.lower() in variations:
                return 1.0
        
        return similarity
    
    def check_weight_similarity(self, name1: str, name2: str) -> float:
        """Check weight/volume similarity between two product names"""
        weight1, unit1 = self.extract_weight_volume(name1)
        weight2, unit2 = self.extract_weight_volume(name2)
        
        if not weight1 or not weight2:
            return 0.0
        
        # Convert to same unit for comparison
        weight1_kg = self._convert_to_kg(weight1, unit1)
        weight2_kg = self._convert_to_kg(weight2, unit2)
        
        if weight1_kg is None or weight2_kg is None:
            return 0.0
        
        # Calculate similarity based on weight difference
        if weight1_kg == weight2_kg:
            return 1.0
        
        # Allow for some tolerance (within 10%)
        tolerance = 0.1
        if abs(weight1_kg - weight2_kg) / max(weight1_kg, weight2_kg) <= tolerance:
            return 0.8
        
        return 0.0
    
    def check_same_brand_weight_match(self, product1: str, product2: str) -> Tuple[bool, float]:
        """Check if two products have the same brand and weight but different flavors"""
        # Extract brand and product info
        brand1, product_info1 = self.extract_brand_and_product(product1)
        brand2, product_info2 = self.extract_brand_and_product(product2)
        
        # Extract weights
        weight1, unit1 = self.extract_weight_volume(product1)
        weight2, unit2 = self.extract_weight_volume(product2)
        
        # Check if brands match
        if not brand1 or not brand2:
            return False, 0.0
        
        brand_similarity = self.check_brand_similarity(product1, product2)
        if brand_similarity < 0.8:  # Require high brand similarity
            return False, 0.0
        
        # Check if weights match exactly
        if weight1 is None or weight2 is None:
            return False, 0.0
        
        # Convert to same unit if possible
        weight1_kg = self._convert_to_kg(weight1, unit1)
        weight2_kg = self._convert_to_kg(weight2, unit2)
        
        if weight1_kg is None or weight2_kg is None:
            return False, 0.0
        
        # Check if weights are exactly the same
        if weight1_kg != weight2_kg:
            return False, 0.0
        
        # Check if flavors are different (this indicates same product line, different variant)
        # Look for flavor indicators in the product names
        flavor_indicators = [
            'tomato', 'chicken', 'beef', 'vegetable', 'mushroom', 'cream', 'cheese',
            'original', 'classic', 'traditional', 'organic', 'reduced', 'light',
            'sweet', 'sour', 'spicy', 'mild', 'hot', 'garlic', 'herb', 'basil',
            'oregano', 'thyme', 'rosemary', 'lemon', 'lime', 'orange', 'berry',
            'strawberry', 'chocolate', 'vanilla', 'caramel', 'coffee', 'mint'
        ]
        
        product1_lower = product1.lower()
        product2_lower = product2.lower()
        
        flavor1 = None
        flavor2 = None
        
        for flavor in flavor_indicators:
            if flavor in product1_lower:
                flavor1 = flavor
            if flavor in product2_lower:
                flavor2 = flavor
        
        # If we found different flavors, this is a good match
        if flavor1 and flavor2 and flavor1 != flavor2:
            return True, 0.85  # High confidence for same brand/weight, different flavor
        
        # If no specific flavors found, check if the product names are different
        # but have the same brand and weight
        if product_info1 != product_info2:
            return True, 0.75  # Medium confidence for same brand/weight, different variant
        
        return False, 0.0
    
    def _convert_to_kg(self, value: float, unit: str) -> Optional[float]:
        """Convert weight/volume to kg/l for comparison"""
        conversions = {
            'g': value / 1000,
            'kg': value,
            'ml': value / 1000,  # Convert ml to liters for liquid comparison
            'l': value,
            'pc': None,  # Pieces can't be converted
            'pack': None,  # Packs can't be converted
            'x': None,  # Multipliers can't be converted
        }
        
        return conversions.get(unit.lower())
    
    def enhanced_product_match(self, product_name: str, scraped_items: List[Dict], 
                             threshold: float = 0.7) -> Optional[ProductMatch]:
        """Match products using multiple criteria with preference for base retail prices"""
        if not scraped_items:
            return None
        
        product_name_clean = self.clean_product_text(product_name)
        best_match = None
        highest_score = 0
        promotional_penalty = 0.3  # Penalty for promotional prices
        
        # First pass: look for exact matches, prioritizing non-promotional
        exact_matches = []
        for item in scraped_items:
            item_name = item.get('name', '')
            if not item_name:
                continue
            
            item_name_clean = self.clean_product_text(item_name)
            
            if product_name_clean == item_name_clean:
                is_promotional = self.is_promotional_price(item_name)
                exact_matches.append((item, is_promotional))
        
        # If we have exact matches, return the best one (non-promotional preferred)
        if exact_matches:
            # Sort by promotional status (non-promotional first)
            exact_matches.sort(key=lambda x: x[1])  # False (non-promotional) comes before True
            return self._create_product_match(exact_matches[0][0], 1.0, 'exact')
        
        # Second pass: look for same brand and weight matches (different flavors)
        same_brand_weight_matches = []
        for item in scraped_items:
            item_name = item.get('name', '')
            if not item_name:
                continue
            
            is_same_brand_weight, confidence = self.check_same_brand_weight_match(product_name, item_name)
            if is_same_brand_weight:
                is_promotional = self.is_promotional_price(item_name)
                same_brand_weight_matches.append((item, confidence, is_promotional))
        
        # If we have same brand/weight matches, return the best one (non-promotional preferred)
        if same_brand_weight_matches:
            # Sort by promotional status first, then by confidence
            same_brand_weight_matches.sort(key=lambda x: (x[2], -x[1]))  # Non-promotional first, then highest confidence
            best_match = same_brand_weight_matches[0]
            return self._create_product_match(best_match[0], best_match[1], 'same_brand_weight')
        
        # Third pass: fuzzy matching with promotional penalty
        for item in scraped_items:
            item_name = item.get('name', '')
            if not item_name:
                continue
            
            item_name_clean = self.clean_product_text(item_name)
            
            # 1. Fuzzy matching
            similarity = fuzz.token_set_ratio(product_name_clean, item_name_clean) / 100.0
            
            # 2. Brand matching
            brand_match = self.check_brand_similarity(product_name, item_name)
            
            # 3. Weight/volume matching
            weight_match = self.check_weight_similarity(product_name, item_name)
            
            # 4. Apply promotional penalty
            is_promotional = self.is_promotional_price(item_name)
            promotional_adjustment = -promotional_penalty if is_promotional else 0
            
            # Combined score with weights and promotional penalty
            total_score = (similarity * 0.6 + brand_match * 0.2 + weight_match * 0.2) + promotional_adjustment
            
            if total_score > highest_score and total_score > threshold:
                highest_score = total_score
                best_match = item
        
        if best_match:
            return self._create_product_match(best_match, highest_score, 'fuzzy')
        
        return None
    
    def _create_product_match(self, item: Dict, confidence: float, match_type: str) -> ProductMatch:
        """Create a ProductMatch object from scraped item"""
        name = item.get('name', '')
        price = self._extract_price(item)
        unit_price = self._extract_unit_price(item)
        weight, _ = self.extract_weight_volume(name)
        
        # Validate the match
        validation_issues = self.validate_price_extraction(name, price, unit_price, weight)
        
        return ProductMatch(
            name=name,
            price=price,
            unit_price=unit_price,
            weight=weight,
            confidence=confidence,
            match_type=match_type,
            validation_issues=validation_issues,
            retailer=item.get('retailer', 'Unknown'),
            url=item.get('url')
        )
    
    def _extract_price(self, item: Dict) -> Optional[float]:
        """Extract price from item data"""
        # Check if price is already a number (from trolley scraper)
        price_value = item.get('price')
        if isinstance(price_value, (int, float)) and price_value > 0:
            return float(price_value)
        
        # If not a number, try to extract from text
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
    
    def _extract_unit_price(self, item: Dict) -> Optional[float]:
        """Extract unit price from item data"""
        unit_price_text = item.get('unit_price', '') or item.get('price_per_unit', '')
        if not unit_price_text:
            return None
        
        # Unit price patterns
        unit_patterns = [
            r'£(\d+\.\d{2})/(kg|g|ml|l|pc)',
            r'(\d+\.\d{2})p/(kg|g|ml|l|pc)',
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, str(unit_price_text))
            if match:
                value = float(match.group(1))
                if 'p' in pattern:
                    value /= 100  # Convert pence to pounds
                return value
        
        return None
    
    def validate_price_extraction(self, product_name: str, price: Optional[float], 
                                unit_price: Optional[float], weight: Optional[float]) -> List[str]:
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
        
        # Unit price sanity check
        if unit_price and weight:
            calculated_unit = price / weight * 1000  # per kg/l
            if abs(calculated_unit - unit_price) > calculated_unit * 0.5:
                validation_issues.append(
                    f"Unit price £{unit_price:.2f} doesn't match calculated value £{calculated_unit:.2f}"
                )
        
        # Weight sanity check - adjusted for common product weights
        if weight and weight > 5000:  # More than 5kg is suspicious for most products
            validation_issues.append(f"Unusually large weight/volume: {weight}")
        
        return validation_issues


class MLProductMatcher:
    """Machine Learning based product matcher"""
    
    def __init__(self):
        if not ML_AVAILABLE:
            raise ImportError("scikit-learn is required for ML features")
        
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        self.product_vectors = None
        self.product_names = []
    
    def train(self, product_names: List[str]):
        """Train on known product names"""
        if not product_names:
            return
        
        # Clean product names
        cleaned_names = [self._clean_text(name) for name in product_names]
        self.product_names = cleaned_names
        
        # Fit vectorizer and transform
        self.product_vectors = self.vectorizer.fit_transform(cleaned_names)
    
    def find_best_match(self, scraped_name: str, threshold: float = 0.7) -> Tuple[Optional[str], float]:
        """Find best match using cosine similarity"""
        if not self.product_vectors is not None:
            return None, 0.0
        
        cleaned_name = self._clean_text(scraped_name)
        query_vector = self.vectorizer.transform([cleaned_name])
        
        similarities = cosine_similarity(query_vector, self.product_vectors)
        best_match_idx = np.argmax(similarities)
        best_score = similarities[0, best_match_idx]
        
        if best_score > threshold:
            return self.product_names[best_match_idx], best_score
        
        return None, best_score
    
    def _clean_text(self, text: str) -> str:
        """Clean text for ML processing"""
        if not text:
            return ""
        
        # Basic cleaning
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text


# Store-specific parsing functions
def parse_tesco_product(item: Dict) -> Dict:
    """Tesco-specific parsing rules"""
    name = item.get('name', '')
    price_text = item.get('price', '') or item.get('price_text', '')
    
    # Extract price
    price_match = re.search(r'£(\d+\.\d{2})', str(price_text))
    price = float(price_match.group(1)) if price_match else None
    
    # Extract unit price
    unit_price_match = re.search(r'£(\d+\.\d{2})/(kg|g|ml|l|pc)', str(price_text))
    unit_price = float(unit_price_match.group(1)) if unit_price_match else None
    
    # Extract weight
    weight, _ = EnhancedProductMatcher().extract_weight_volume(name)
    
    return {
        'name': EnhancedProductMatcher().clean_product_text(name),
        'price': price,
        'unit_price': unit_price,
        'weight': weight,
        'retailer': 'Tesco'
    }


def parse_sainsburys_product(item: Dict) -> Dict:
    """Sainsbury's specific parsing rules"""
    name = item.get('name', '')
    price_text = item.get('price', '') or item.get('price_text', '')
    
    # Sainsbury's specific patterns
    price_match = re.search(r'£(\d+\.\d{2})', str(price_text))
    price = float(price_match.group(1)) if price_match else None
    
    # Extract weight
    weight, _ = EnhancedProductMatcher().extract_weight_volume(name)
    
    return {
        'name': EnhancedProductMatcher().clean_product_text(name),
        'price': price,
        'unit_price': None,  # Sainsbury's might not show unit price
        'weight': weight,
        'retailer': 'Sainsbury\'s'
    }


def parse_asda_product(item: Dict) -> Dict:
    """ASDA specific parsing rules"""
    name = item.get('name', '')
    price_text = item.get('price', '') or item.get('price_text', '')
    
    # ASDA specific patterns
    price_match = re.search(r'£(\d+\.\d{2})', str(price_text))
    price = float(price_match.group(1)) if price_match else None
    
    # Extract weight
    weight, _ = EnhancedProductMatcher().extract_weight_volume(name)
    
    return {
        'name': EnhancedProductMatcher().clean_product_text(name),
        'price': price,
        'unit_price': None,
        'weight': weight,
        'retailer': 'ASDA'
    }


# Configuration for different retailers
RETAILER_CONFIG = {
    'tesco': {
        'selectors': {
            'product': '[data-auto="product-tile"]',
            'name': 'h3',
            'price': '[data-auto="price-value"]',
            'unit_price': '[data-auto="price-per-quantity-weight"]'
        },
        'url_patterns': {
            'search': 'https://www.tesco.com/groceries/en-GB/search?query={query}'
        },
        'parser': parse_tesco_product
    },
    'sainsburys': {
        'selectors': {
            'product': '.gridItem',
            'name': '.productName',
            'price': '.pricePerUnit',
        },
        'url_patterns': {
            'search': 'https://www.sainsburys.co.uk/shop/gb/groceries/search?searchTerm={query}'
        },
        'parser': parse_sainsburys_product
    },
    'asda': {
        'selectors': {
            'product': '.co-product',
            'name': '.co-product__title',
            'price': '.co-product__price',
        },
        'url_patterns': {
            'search': 'https://groceries.asda.com/api/items/search?keyword={query}'
        },
        'parser': parse_asda_product
    }
}


def parse_retailer_product(item: Dict, retailer: str) -> Dict:
    """Parse product data based on retailer"""
    config = RETAILER_CONFIG.get(retailer.lower())
    if config and config.get('parser'):
        return config['parser'](item)
    
    # Default parsing
    matcher = EnhancedProductMatcher()
    return {
        'name': matcher.clean_product_text(item.get('name', '')),
        'price': matcher._extract_price(item),
        'unit_price': matcher._extract_unit_price(item),
        'weight': matcher.extract_weight_volume(item.get('name', ''))[0],
        'retailer': retailer
    }
