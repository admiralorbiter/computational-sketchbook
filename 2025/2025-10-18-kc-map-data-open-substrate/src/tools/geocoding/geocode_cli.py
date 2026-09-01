#!/usr/bin/env python3
"""
Geocoding CLI Tool

Command-line interface for managing and testing the geocoding service.
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.geocoding.geocoding_service import GeocodingService
from tools.database.create_geocoding_cache import create_geocoding_cache_table

def geocode_single_address(address: str, db_path: str, google_api_key: str = None):
    """Geocode a single address"""
    print(f"Geocoding: {address}")
    print("-" * 50)
    
    service = GeocodingService(db_path, google_api_key)
    result = service.geocode_address(address)
    
    if result['success']:
        print(f"[SUCCESS] Geocoded successfully!")
        print(f"   Coordinates: {result['latitude']}, {result['longitude']}")
        print(f"   Formatted: {result['formatted_address']}")
        print(f"   Confidence: {result['confidence_score']:.1f}%")
        print(f"   Quality: {result['geocoding_quality']}")
        print(f"   Source: {result['source']}")
        print(f"   From Cache: {result['from_cache']}")
        if result.get('times_used', 0) > 1:
            print(f"   Times Used: {result['times_used']}")
    else:
        print(f"[FAILED] {result['error']}")

def geocode_batch_file(file_path: str, db_path: str, google_api_key: str = None, output_file: str = None):
    """Geocode addresses from a CSV file"""
    print(f"Processing batch file: {file_path}")
    print("-" * 50)
    
    service = GeocodingService(db_path, google_api_key)
    
    # Read addresses from CSV
    addresses = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Look for address column (try common names)
                address = None
                for col in ['address', 'Address', 'ADDRESS', 'full_address', 'location']:
                    if col in row and row[col]:
                        address = row[col]
                        break
                
                if address:
                    addresses.append(address)
        
        print(f"Found {len(addresses)} addresses to geocode")
        
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return
    
    # Geocode addresses
    results = service.batch_geocode(addresses)
    
    # Count results
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\nBatch geocoding complete:")
    print(f"   Total: {len(results)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Success rate: {successful/len(results)*100:.1f}%")
    
    # Save results if output file specified
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['address', 'latitude', 'longitude', 'confidence_score', 'quality', 'source', 'success', 'error'])
                
                for i, result in enumerate(results):
                    writer.writerow([
                        addresses[i],
                        result.get('latitude', ''),
                        result.get('longitude', ''),
                        result.get('confidence_score', ''),
                        result.get('geocoding_quality', ''),
                        result.get('source', ''),
                        result['success'],
                        result.get('error', '')
                    ])
            
            print(f"Results saved to: {output_file}")
            
        except Exception as e:
            print(f"[ERROR] Error saving results: {e}")

def backfill_table(table_name: str, db_path: str, google_api_key: str = None, limit: int = None):
    """Geocode missing coordinates in a database table"""
    print(f"Backfilling coordinates for table: {table_name}")
    print("-" * 50)
    
    service = GeocodingService(db_path, google_api_key)
    
    # This would need to be implemented based on your specific table structure
    # For now, just show a placeholder
    print("[WARNING] Backfill functionality needs to be implemented based on your table structure")
    print("   This would involve:")
    print("   1. Finding records with addresses but no coordinates")
    print("   2. Geocoding those addresses")
    print("   3. Updating the records with coordinates")

def show_stats(db_path: str):
    """Show cache and usage statistics"""
    print("Geocoding Service Statistics")
    print("=" * 50)
    
    service = GeocodingService(db_path)
    
    # Cache stats
    print("\n=== Cache Statistics ===")
    cache_stats = service.get_cache_stats()
    print(f"   Total cached addresses: {cache_stats['total_cached']:,}")
    print(f"   Census geocoded: {cache_stats['census_cached']:,}")
    print(f"   Google geocoded: {cache_stats['google_cached']:,}")
    print(f"   High quality: {cache_stats['high_quality']:,}")
    print(f"   Medium quality: {cache_stats['medium_quality']:,}")
    print(f"   Low quality: {cache_stats['low_quality']:,}")
    print(f"   Average confidence: {cache_stats['avg_confidence']:.1f}%")
    
    if cache_stats['most_used']:
        print(f"\n   Most used addresses:")
        for addr, count in cache_stats['most_used'][:5]:
            print(f"     {count}x: {addr}")
    
    # Usage stats
    print(f"\n=== Usage Statistics ===")
    usage_stats = service.get_usage_stats()
    print(f"   Total requests: {usage_stats['total_requests']:,}")
    print(f"   Overall success rate: {usage_stats['overall_success_rate']:.1f}%")
    
    for service_name, stats in usage_stats['services'].items():
        print(f"\n   {service_name.upper()} API:")
        print(f"     Requests today: {stats['request_count']:,}")
        print(f"     Success rate: {stats['success_rate']:.1f}%")
        print(f"     Remaining: {stats['remaining_requests']:,}")
        print(f"     Within limit: {stats['within_limit']}")
        if stats['approaching_limit']:
            print(f"     [WARNING] Approaching limit!")

def show_failed_addresses(db_path: str, limit: int = 50):
    """Show addresses that failed to geocode"""
    print("Failed Geocoding Addresses")
    print("=" * 50)
    
    service = GeocodingService(db_path)
    failed_addresses = service.get_failed_addresses(limit)
    
    if not failed_addresses:
        print("No failed addresses found")
        return
    
    print(f"Found {len(failed_addresses)} failed addresses:")
    print()
    
    for i, failure in enumerate(failed_addresses, 1):
        print(f"{i}. {failure['original_address']}")
        print(f"   Error: {failure['error_message']}")
        print(f"   Source: {failure['geocoding_source'] or 'Unknown'}")
        print(f"   Retry count: {failure['retry_count']}")
        print(f"   Last attempt: {failure['last_attempt']}")
        print()

def show_failure_stats(db_path: str):
    """Show failure statistics"""
    print("Failed Geocoding Statistics")
    print("=" * 50)
    
    service = GeocodingService(db_path)
    stats = service.get_failure_stats()
    
    print(f"Total failures: {stats['total_failures']}")
    print(f"Recent failures (7 days): {stats['recent_failures']}")
    
    if stats['error_breakdown']:
        print("\nError breakdown:")
        for error, count in stats['error_breakdown'].items():
            print(f"  {error}: {count}")
    
    if stats['source_breakdown']:
        print("\nSource breakdown:")
        for source, count in stats['source_breakdown'].items():
            print(f"  {source}: {count}")
    
    if stats['retry_distribution']:
        print("\nRetry distribution:")
        for retry_count, count in stats['retry_distribution'].items():
            print(f"  {retry_count} retries: {count}")

def retry_failed_addresses(db_path: str, limit: int = 50):
    """Retry geocoding failed addresses"""
    print(f"Retrying {limit} failed addresses...")
    print("-" * 50)
    
    service = GeocodingService(db_path)
    results = service.retry_failed_addresses(limit)
    
    print(f"Retry Results:")
    print(f"  Total retried: {results['total_retried']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Still failed: {results['still_failed']}")
    print(f"  Errors: {results['errors']}")

def clear_cache(db_path: str, confirm: bool = False):
    """Clear the geocoding cache"""
    if not confirm:
        print("[WARNING] This will delete ALL cached geocoding data!")
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print("Operation cancelled")
            return
    
    service = GeocodingService(db_path)
    service.clear_cache(confirm=True)
    print("[SUCCESS] Cache cleared")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Geocoding Service CLI Tool")
    
    # Global options
    parser.add_argument('--db-path', default='data/processed/kc_data.gpkg',
                       help='Path to database file')
    parser.add_argument('--google-api-key', 
                       help='Google Maps API key (or set GOOGLE_MAPS_API_KEY env var)')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Geocode single address
    geocode_parser = subparsers.add_parser('geocode', help='Geocode a single address')
    geocode_parser.add_argument('address', help='Address to geocode')
    
    # Batch geocode from file
    batch_parser = subparsers.add_parser('batch', help='Geocode addresses from CSV file')
    batch_parser.add_argument('file', help='CSV file with addresses')
    batch_parser.add_argument('--output', help='Output CSV file for results')
    
    # Backfill table
    backfill_parser = subparsers.add_parser('backfill', help='Geocode missing coordinates in table')
    backfill_parser.add_argument('table', help='Table name to backfill')
    backfill_parser.add_argument('--limit', type=int, help='Limit number of records to process')
    
    # Show statistics
    stats_parser = subparsers.add_parser('stats', help='Show cache and usage statistics')
    
    # Show failed addresses
    failed_parser = subparsers.add_parser('failed', help='Show failed geocoding addresses')
    failed_parser.add_argument('--limit', type=int, default=50, help='Limit number of failed addresses to show')
    
    # Show failure statistics
    failure_stats_parser = subparsers.add_parser('failure-stats', help='Show failure statistics')
    
    # Retry failed addresses
    retry_parser = subparsers.add_parser('retry', help='Retry geocoding failed addresses')
    retry_parser.add_argument('--limit', type=int, default=50, help='Limit number of addresses to retry')
    
    # Clear cache
    clear_parser = subparsers.add_parser('clear-cache', help='Clear geocoding cache')
    clear_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Get Google API key
    google_api_key = args.google_api_key or os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # Ensure database exists
    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"Creating database: {db_path}")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        create_geocoding_cache_table(str(db_path))
    
    # Execute command
    try:
        if args.command == 'geocode':
            geocode_single_address(args.address, str(db_path), google_api_key)
        
        elif args.command == 'batch':
            geocode_batch_file(args.file, str(db_path), google_api_key, args.output)
        
        elif args.command == 'backfill':
            backfill_table(args.table, str(db_path), google_api_key, args.limit)
        
        elif args.command == 'stats':
            show_stats(str(db_path))
        
        elif args.command == 'failed':
            show_failed_addresses(str(db_path), args.limit)
        
        elif args.command == 'failure-stats':
            show_failure_stats(str(db_path))
        
        elif args.command == 'retry':
            retry_failed_addresses(str(db_path), args.limit)
        
        elif args.command == 'clear-cache':
            clear_cache(str(db_path), args.confirm)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
