# 🐱 Meow - Spicy Cat Photo Downloader

Welcome to the meow folder! This directory contains scripts to download cat photos from the Cat API.

## 📦 What's Inside

- **50 Pre-downloaded Cat Photos**: `spicy-cat-01.jpg` through `spicy-cat-50.jpg`
- **Python Download Script**: `get_cats.py` - Interactive Python script
- **Bash Download Script**: `get_cats.sh` - Interactive Bash script

## 🚀 Quick Start

### Using Python Script

```bash
# Run the Python script
./get_cats.py

# Or with python3
python3 get_cats.py
```

**Requirements:**
- Python 3.x
- `requests` library (install with: `pip install requests`)

### Using Bash Script

```bash
# Run the Bash script
./get_cats.sh

# Or with bash
bash get_cats.sh
```

**Requirements:**
- `curl` command (usually pre-installed)
- `bc` command (for size calculations, optional)

## 📖 How It Works

1. **Prompt**: The script asks how many cat photos you want
2. **Create Directory**: A timestamped folder is created (e.g., `downloaded_cats_20260206_143000`)
3. **Download**: Photos are downloaded from https://cataas.com/cat
4. **Summary**: Statistics are shown when complete

## 🎯 Features

- ✅ User-prompted quantity selection
- ✅ Progress tracking with real-time feedback
- ✅ Timestamped output directories
- ✅ File size reporting
- ✅ Download summary statistics
- ✅ Cat jokes in code comments! 🎭
- ✅ Error handling and retry logic
- ✅ API rate limiting (0.3s delay between requests)

## 📝 Example Output

```
==================================================
🌶️  SPICY CAT PHOTO DOWNLOADER 🌶️
==================================================

Welcome to the ultimate cat photo downloader!
Using the Cat API to fetch adorable feline friends.

🐱 How many spicy cat photos do you want to download? 5

📁 Created directory: downloaded_cats_20260206_143000

🚀 Starting download of 5 spicy cat photos...
==================================================
✅ [1/5] Downloaded spicy-cat-001.jpg (234.5 KB)
✅ [2/5] Downloaded spicy-cat-002.jpg (156.2 KB)
✅ [3/5] Downloaded spicy-cat-003.jpg (312.8 KB)
✅ [4/5] Downloaded spicy-cat-004.jpg (198.4 KB)
✅ [5/5] Downloaded spicy-cat-005.jpg (267.1 KB)

==================================================
📊 DOWNLOAD SUMMARY
==================================================
✅ Successful downloads: 5
❌ Failed downloads: 0
📦 Total size: 1.14 MB
📁 Location: downloaded_cats_20260206_143000/
==================================================

🎉 Your spicy cat photos are ready!
```

## 🌐 API Information

This script uses the free Cat as a Service (cataas) API:
- **URL**: https://cataas.com
- **Endpoint**: https://cataas.com/cat
- **No API key required**
- **Free to use**

## 🤝 Contributing

Feel free to enhance these scripts with:
- Additional cat API support (The Cat API, Random Cat, etc.)
- Custom filtering options (breed, tags, size)
- Image format selection
- Parallel downloads for faster performance

## 📜 License

Part of the spicy-cat repository. Use responsibly and enjoy your cat photos! 🐈
