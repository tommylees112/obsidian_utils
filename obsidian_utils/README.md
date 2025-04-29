# Obsidian Image Compression Utility

A utility for compressing PNG images in your Obsidian vault while maintaining a safe backup of original images.

## Features

- Scan and backup all PNG images in your Obsidian vault
- Compress images using pngquant
- Calculate space savings
- Safe overwrite of original images
- Full undo capability
- Detailed compression reports
- Progress bars and logging

## Prerequisites

- Python 3.8 or later
- [pngquant](https://pngquant.org/) installed and in your PATH

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/obsidian-utils.git
cd obsidian-utils
```

2. Install the package:
```bash
pip install -e .
```

## Usage

### 1. Find and compress images
```bash
compress-images run --obsidian-dir /path/to/vault
```

### 2. Overwrite originals with compressed versions
```bash
compress-images overwrite --run-id 20240429_1535
```

### 3. Undo and restore originals
```bash
compress-images undo --run-id 20240429_1535
```

### 4. Clean up all backups and processed files
```bash
compress-images cleanup --run-id 20240429_1535
```

## Configuration

The compression can be configured with the following options:

- `--quality-min`: Minimum quality (0-100), default 65
- `--quality-max`: Maximum quality (0-100), default 80
- `--speed`: Compression speed (1-11), default 1 (slowest but best compression)

## Folder Structure

```
data/
└── 20240429_1535/        # run_id
    ├── raw/              # original images backup
    │   └── nested/paths/image1.png
    ├── processed/        # compressed images
    │   └── nested/paths/image1.png
    ├── image_paths.txt  # list of processed images
    └── summary.json     # compression statistics
```

## License

MIT 