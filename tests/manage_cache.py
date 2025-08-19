#!/usr/bin/env python3
"""
Cache Management Script
======================
Manage the scraper cache
"""

import sys
import os
import argparse

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.cache_manager import CacheManager


def main():
    """Main function for cache management"""
    parser = argparse.ArgumentParser(description='Manage scraper cache')
    parser.add_argument('action', choices=['stats', 'clear', 'info'], 
                       help='Action to perform: stats (show cache stats), clear (clear cache), info (show cache info)')
    parser.add_argument('--cache-dir', default='cache', help='Cache directory (default: cache)')
    parser.add_argument('--cache-duration', type=int, default=24, help='Cache duration in hours (default: 24)')
    
    args = parser.parse_args()
    
    # Initialize cache manager
    cache_manager = CacheManager(cache_dir=args.cache_dir, cache_duration_hours=args.cache_duration)
    
    if args.action == 'stats':
        print("📊 Cache Statistics:")
        cache_manager.print_cache_stats()
        
    elif args.action == 'clear':
        print("🗑️ Clearing cache...")
        cache_manager.clear_cache()
        print("✅ Cache cleared successfully!")
        
    elif args.action == 'info':
        print("ℹ️ Cache Information:")
        print(f"   Cache directory: {args.cache_dir}")
        print(f"   Cache duration: {args.cache_duration} hours")
        print(f"   Search cache file: {cache_manager.search_cache_file}")
        print(f"   Price cache file: {cache_manager.price_cache_file}")
        
        # Check if cache files exist
        search_exists = os.path.exists(cache_manager.search_cache_file)
        price_exists = os.path.exists(cache_manager.price_cache_file)
        
        print(f"   Search cache file exists: {'✅ Yes' if search_exists else '❌ No'}")
        print(f"   Price cache file exists: {'✅ Yes' if price_exists else '❌ No'}")
        
        if search_exists:
            search_size = os.path.getsize(cache_manager.search_cache_file)
            print(f"   Search cache file size: {search_size:,} bytes")
        
        if price_exists:
            price_size = os.path.getsize(cache_manager.price_cache_file)
            print(f"   Price cache file size: {price_size:,} bytes")


if __name__ == "__main__":
    main()
