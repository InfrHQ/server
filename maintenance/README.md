# Maintenance Tools

This directory contains a collection of scripts and tools designed to help maintain, diagnose, and monitor the Infr server's performance and health. 

## Contents

### WebP Statistics Tool (`webp_stats.py`)

This script navigates through the `storage/segments` directory, looks for `image.webp` files in each segment directory, and gathers statistics about their file sizes, such as:

- Average size
- Median size
- Standard Deviation
- Min & Max sizes

**Usage**:
```bash
python3 maintenance/webp_stats.py
```