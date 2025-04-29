"""Configuration and summary dataclasses for image compression."""
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict, Optional

@dataclass
class PngquantConfig:
    """Configuration for pngquant compression."""
    quality_min: int = 65
    quality_max: int = 80
    speed: int = 1
    strip_metadata: bool = True
    force: bool = True
    skip_if_larger: bool = False
    verbose: bool = False
    no_dithering: bool = False
    posterize: Optional[int] = None

    def to_cli_args(self) -> List[str]:
        """Convert config into a list of pngquant CLI arguments."""
        args = []
        args.append(f"--quality={self.quality_min}-{self.quality_max}")
        args.append(f"--speed={self.speed}")
        if self.strip_metadata:
            args.append("--strip")
        if self.force:
            args.append("--force")
        if self.skip_if_larger:
            args.append("--skip-if-larger")
        if self.verbose:
            args.append("--verbose")
        if self.no_dithering:
            args.append("--nofs")
        if self.posterize is not None:
            args.append(f"--posterize={self.posterize}")
        return args

@dataclass
class CompressionSummary:
    """Summary of a compression run."""
    run_id: str
    timestamp: str
    obsidian_dir: str
    config: PngquantConfig
    total_images: int
    raw_size_bytes: int
    compressed_size_bytes: int
    space_saved_bytes: int
    space_saved_percent: float
    failed_images: List[str]

    def to_dict(self) -> Dict:
        """Convert summary to dictionary for JSON serialization."""
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "obsidian_dir": str(self.obsidian_dir),
            "config": vars(self.config),
            "total_images": self.total_images,
            "raw_size_bytes": self.raw_size_bytes,
            "compressed_size_bytes": self.compressed_size_bytes,
            "space_saved_bytes": self.space_saved_bytes,
            "space_saved_percent": self.space_saved_percent,
            "failed_images": self.failed_images
        }

    def save(self, run_dir: Path) -> None:
        """Save summary to JSON file."""
        summary_path = run_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2) 