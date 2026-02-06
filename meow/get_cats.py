#!/usr/bin/env python3
"""
Spicy Cat Photo Downloader
Download cat photos from the Cat API with custom quantity
"""

import os
import sys
import time
import requests
from datetime import datetime

# Why don't cats play poker in the jungle? Too many cheetahs!
def get_user_input():
    """Prompt user for the number of cat photos to download"""
    while True:
        try:
            quantity = input("\n🐱 How many spicy cat photos do you want to download? ")
            num = int(quantity)
            if num <= 0:
                print("❌ Please enter a positive number!")
                continue
            if num > 200:
                confirm = input(f"⚠️  That's a lot of cats! Are you sure you want {num} photos? (yes/no): ")
                if confirm.lower() not in ['yes', 'y']:
                    continue
            return num
        except ValueError:
            print("❌ Please enter a valid number!")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

# What's a cat's favorite color? Purrrple!
def create_output_directory():
    """Create a timestamped directory for downloaded photos"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"downloaded_cats_{timestamp}"

    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Created directory: {output_dir}")
        return output_dir
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        sys.exit(1)

# How do cats end a fight? They hiss and make up!
def download_cat_photo(photo_num, output_dir, session):
    """Download a single cat photo from the API"""
    try:
        # Add timestamp and random number to ensure unique photos
        url = f"https://cataas.com/cat?timestamp={int(time.time())}{photo_num}"

        response = session.get(url, timeout=10)
        response.raise_for_status()

        filename = os.path.join(output_dir, f"spicy-cat-{photo_num:03d}.jpg")

        with open(filename, 'wb') as f:
            f.write(response.content)

        file_size = len(response.content) / 1024  # Convert to KB
        return True, file_size

    except Exception as e:
        return False, str(e)

# What do you call a pile of cats? A meow-tain!
def download_all_cats(quantity, output_dir):
    """Download all requested cat photos with progress tracking"""
    print(f"\n🚀 Starting download of {quantity} spicy cat photos...")
    print("=" * 50)

    successful = 0
    failed = 0
    total_size = 0

    # Use a session for better performance
    session = requests.Session()

    for i in range(1, quantity + 1):
        success, result = download_cat_photo(i, output_dir, session)

        if success:
            successful += 1
            total_size += result
            print(f"✅ [{i}/{quantity}] Downloaded spicy-cat-{i:03d}.jpg ({result:.1f} KB)")
        else:
            failed += 1
            print(f"❌ [{i}/{quantity}] Failed to download: {result}")

        # Small delay to be nice to the API
        if i < quantity:
            time.sleep(0.3)

    return successful, failed, total_size

# Why did the cat run from the tree? Because it was afraid of the bark!
def print_summary(successful, failed, total_size, output_dir):
    """Print download summary statistics"""
    print("\n" + "=" * 50)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 50)
    print(f"✅ Successful downloads: {successful}")
    print(f"❌ Failed downloads: {failed}")
    print(f"📦 Total size: {total_size / 1024:.2f} MB")
    print(f"📁 Location: {output_dir}/")
    print("=" * 50)

    if successful > 0:
        print("\n🎉 Your spicy cat photos are ready!")
    else:
        print("\n😿 No photos were downloaded. Please check your internet connection.")

# What do cats like to eat for breakfast? Mice Krispies!
def main():
    """Main function to orchestrate the cat photo download process"""
    print("=" * 50)
    print("🌶️  SPICY CAT PHOTO DOWNLOADER 🌶️")
    print("=" * 50)
    print("\nWelcome to the ultimate cat photo downloader!")
    print("Using the Cat API to fetch adorable feline friends.")

    # Get user input
    quantity = get_user_input()

    # Create output directory
    output_dir = create_output_directory()

    # Download all the cats!
    successful, failed, total_size = download_all_cats(quantity, output_dir)

    # Show summary
    print_summary(successful, failed, total_size, output_dir)

# Why are cats good at video games? Because they have nine lives!
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Download interrupted by user.")
        print("👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 An unexpected error occurred: {e}")
        sys.exit(1)
