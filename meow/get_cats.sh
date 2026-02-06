#!/bin/bash
################################################################################
# Spicy Cat Photo Downloader (Bash Version)
# Download cat photos from the Cat API with custom quantity
################################################################################

set -e  # Exit on error

# What's a cat's favorite button on the TV remote? Paws!
prompt_user_for_quantity() {
    while true; do
        echo ""
        read -p "🐱 How many spicy cat photos do you want to download? " quantity

        # Check if input is a number
        if ! [[ "$quantity" =~ ^[0-9]+$ ]]; then
            echo "❌ Please enter a valid number!"
            continue
        fi

        # Check if positive
        if [ "$quantity" -le 0 ]; then
            echo "❌ Please enter a positive number!"
            continue
        fi

        # Warn for large quantities
        if [ "$quantity" -gt 200 ]; then
            read -p "⚠️  That's a lot of cats! Are you sure you want $quantity photos? (yes/no): " confirm
            if [[ ! "$confirm" =~ ^[yY]([eE][sS])?$ ]]; then
                continue
            fi
        fi

        echo "$quantity"
        return 0
    done
}

# Why don't cats like online shopping? They prefer a cat-alogue!
create_output_directory() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local output_dir="downloaded_cats_${timestamp}"

    if mkdir -p "$output_dir"; then
        echo "📁 Created directory: $output_dir" >&2
        echo "$output_dir"
    else
        echo "❌ Error creating directory" >&2
        exit 1
    fi
}

# What do you call a cat who loves to bowl? An alley cat!
download_single_cat() {
    local photo_num=$1
    local output_dir=$2
    local total_count=$3
    local filename=$(printf "${output_dir}/spicy-cat-%03d.jpg" "$photo_num")

    # Use timestamp and photo number for uniqueness
    local url="https://cataas.com/cat?timestamp=$(date +%s)${photo_num}"

    if curl -s -f -o "$filename" "$url"; then
        local file_size=$(du -k "$filename" | cut -f1)
        echo "✅ [$photo_num/$total_count] Downloaded $(basename $filename) (${file_size} KB)" >&2
        return 0
    else
        echo "❌ [$photo_num/$total_count] Failed to download" >&2
        rm -f "$filename"  # Remove partial file
        return 1
    fi
}

# Why did the cat join the Red Cross? She wanted to be a first-aid kit!
download_all_cats() {
    local quantity=$1
    local output_dir=$2
    local successful=0
    local failed=0

    echo "" >&2
    echo "🚀 Starting download of $quantity spicy cat photos..." >&2
    echo "==================================================" >&2

    for ((i=1; i<=quantity; i++)); do
        if download_single_cat "$i" "$output_dir" "$quantity"; then
            ((successful++))
        else
            ((failed++))
        fi

        # Small delay to be nice to the API
        if [ "$i" -lt "$quantity" ]; then
            sleep 0.3
        fi
    done

    echo "$successful $failed"
}

# What's a cat's favorite magazine? Good Mousekeeping!
calculate_total_size() {
    local output_dir=$1
    local total_kb=$(du -sk "$output_dir" | cut -f1)
    local total_mb=$(echo "scale=2; $total_kb / 1024" | bc)
    echo "$total_mb"
}

# How do cats greet each other? "Mice to meet you!"
print_summary() {
    local successful=$1
    local failed=$2
    local output_dir=$3
    local total_mb=$4

    echo ""
    echo "=================================================="
    echo "📊 DOWNLOAD SUMMARY"
    echo "=================================================="
    echo "✅ Successful downloads: $successful"
    echo "❌ Failed downloads: $failed"
    echo "📦 Total size: ${total_mb} MB"
    echo "📁 Location: ${output_dir}/"
    echo "=================================================="

    if [ "$successful" -gt 0 ]; then
        echo ""
        echo "🎉 Your spicy cat photos are ready!"
    else
        echo ""
        echo "😿 No photos were downloaded. Please check your internet connection."
    fi
}

# What do you call a cat that lives in an igloo? An eskimew!
main() {
    echo "=================================================="
    echo "🌶️  SPICY CAT PHOTO DOWNLOADER 🌶️"
    echo "=================================================="
    echo ""
    echo "Welcome to the ultimate cat photo downloader!"
    echo "Using the Cat API to fetch adorable feline friends."

    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        echo "❌ Error: curl is not installed. Please install curl first."
        exit 1
    fi

    # Check if bc is installed (for calculations)
    if ! command -v bc &> /dev/null; then
        echo "⚠️  Warning: bc is not installed. Size calculations may not work."
    fi

    # Get user input
    quantity=$(prompt_user_for_quantity)

    # Create output directory
    output_dir=$(create_output_directory)

    # Download all the cats!
    read successful failed <<< $(download_all_cats "$quantity" "$output_dir")

    # Calculate total size
    total_mb=$(calculate_total_size "$output_dir")

    # Show summary
    print_summary "$successful" "$failed" "$output_dir" "$total_mb"
}

# What did the cat say when it was confused? "I'm purr-plexed!"
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
