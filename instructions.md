📄 Obsidian Image Compression Pipeline Documentation

✨ Overview

This utility is designed to compress .png images inside an Obsidian vault to save disk space, while maintaining a safe backup of original images for full undo capability.

It uses:
	•	pngquant for compression
	•	tqdm for progress bars
	•	loguru for logging
	•	click for the command-line interface
	•	pathlib for path handling
	•	uv for dependency and environment management

⸻

🛠️ Pipeline Stages

1. Scan and Copy
	•	Traverse the provided obsidian_dir.
	•	Find all .png files recursively.
	•	For each file:
	•	Copy it to data/{run_id}/raw/, preserving folder structure relative to obsidian_dir.
	•	Record a list of original file paths for tracking.

2. Compress
	•	Use pngquant to compress each copied image.
	•	Store the compressed versions in data/{run_id}/processed/, again preserving folder structure.
	•	Compression parameters are configurable, but defaults are:
	•	--quality=65-80
	•	--speed=1
	•	If a file is missing during compression (e.g., user deleted or moved it), skip it gracefully and log a warning.

3. Report Compression Results
	•	Calculate:
	•	Total size of raw/ images
	•	Total size of processed/ images
	•	Space saved in bytes and percentage.
	•	Log and print a nice summary report.

4. Overwrite Originals
	•	Copy the compressed images from processed/ back to the original obsidian_dir paths.
	•	Overwrite the original .png files.

5. Undo (Restore)
	•	If needed, restore all original images from raw/ back to their original paths.
	•	Guarantees full reversibility of the compression operation.

6. Cleanup
	•	Remove the entire data/{run_id}/ directory, only when the user manually triggers cleanup.

⸻

⚙️ Configuration

Parameter	Default	Description
--quality	65-80	PNG compression quality range
--speed	1	Compression speed (lower = better compression, slower)
--run-id	auto-generated	Timestamp-based ID for each session (e.g., 20250429_1535)
--obsidian-dir	required	Path to your Obsidian vault folder



⸻

🧹 Important Notes
	•	Auto-generated run_id based on the timestamp to ensure uniqueness.
	•	Raw backups are always stored safely in data/{run_id}/raw/ until explicitly cleaned.
	•	Skipping missing files:
	•	If an image disappears between copy and compress steps (unlikely in normal cases), it will simply continue processing without failing.
	•	Overwrite and undo are manual operations via CLI commands.
	•	No automatic overwriting or irreversible actions unless explicitly confirmed.

⸻

🖥️ Example CLI Usage

# 1. Find and compress images
`compress-images run --obsidian-dir /path/to/vault`

# 2. Overwrite originals with compressed versions
`compress-images overwrite --run-id 20250429_1535`

# 3. Undo and restore originals
`compress-images undo --run-id 20250429_1535`

# 4. Clean up all backups and processed files
`compress-images cleanup --run-id 20250429_1535`



⸻

📂 Folder Structure Example

data/
└── 20250429_1535/        # run_id
    ├── raw/              # original images backup
    │   └── nested/paths/image1.png
    ├── processed/        # compressed images
    │   └── nested/paths/image1.png



⸻

📢 Future Improvements Ideas
	•	Add parallel processing of images for very large vaults
	•	Optional WebP conversion for even better space savings
	•	Slack/Webhook notifications after processing

⸻

✅ Status

This document serves as the official specification and operating procedure for the Obsidian image compression utility.

⸻

Would you also like me to build an auto-run confirmation file (like saving the run stats to data/{run_id}/summary.json) so that it’s easier to review a history of compression jobs? 📄🚀
Let me know! (it’s very easy to add)

# pngquant usage
```
Usage: pngquant [options] [ncolors] -- file [file...]
Options:
  --quality min-max     min and max quality (0-100)
  --speed N             speed/quality tradeoff (1=slow, 11=fast)
  --nofs                disable Floyd–Steinberg dithering
  --strip               remove optional metadata
  --output PATH         save file to path
  --ext EXT             set file extension (default -fs8.png)
  --force               overwrite existing output files
  --skip-if-larger      skip writing output if it's larger
  --posterize N         reduce number of distinct colors
  --verbose             verbose output
  --quiet               suppress output
  --log-level LEVEL     set log verbosity
```

Extra Desirables:
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PngquantConfig:
    quality_min: int = 65           # Minimum quality (0-100)
    quality_max: int = 80           # Maximum quality (0-100)
    speed: int = 1                  # Speed setting (1-11)
    strip_metadata: bool = True     # Remove metadata (EXIF, text chunks, etc.)
    force: bool = True              # Overwrite existing files
    ext: str = ".png"               # File extension for output
    skip_if_larger: bool = False    # Skip saving if output is larger
    verbose: bool = False           # Verbose output
    no_dithering: bool = False      # Disable Floyd–Steinberg dithering
    posterize: Optional[int] = None # Posterization (optional advanced setting)

    def to_cli_args(self) -> list[str]:
        """Convert config into a list of pngquant CLI arguments."""
        args = []
        
        # Quality range
        args.append(f"--quality={self.quality_min}-{self.quality_max}")
        
        # Speed
        args.append(f"--speed={self.speed}")
        
        # Metadata stripping
        if self.strip_metadata:
            args.append("--strip")
        
        # Force overwrite
        if self.force:
            args.append("--force")
        
        # Extension setting
        if self.ext:
            args.append(f"--ext={self.ext}")
        
        # Skip if larger
        if self.skip_if_larger:
            args.append("--skip-if-larger")
        
        # Verbosity
        if self.verbose:
            args.append("--verbose")
        
        # No dithering
        if self.no_dithering:
            args.append("--nofs")
        
        # Posterize
        if self.posterize is not None:
            args.append(f"--posterize={self.posterize}")
        
        return args
```