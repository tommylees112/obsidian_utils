"""Core image processing utilities."""
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from loguru import logger
from tqdm import tqdm

from .config import PngquantConfig, CompressionSummary

DATA_DIR = Path("data")

def generate_run_id() -> str:
    """Generate a unique run ID based on timestamp."""
    return datetime.now().strftime("%Y%m%d_%H%M")

def save_image_paths(run_dir: Path, image_paths: List[Path]) -> None:
    """Save list of processed image paths to a file."""
    paths_file = run_dir / "image_paths.txt"
    with open(paths_file, 'w') as f:
        for path in image_paths:
            f.write(f"{path}\n")

def scan_and_copy_images(obsidian_dir: Path, run_id: str) -> List[Path]:
    """Scan obsidian directory for PNGs and copy to backup."""
    raw_dir = DATA_DIR / run_id / "raw"
    raw_paths = []
    
    for png_path in tqdm(list(obsidian_dir.rglob("*.png")), desc="Copying images"):
        rel_path = png_path.relative_to(obsidian_dir)
        dest_path = raw_dir / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png_path, dest_path)
        raw_paths.append(rel_path)
    
    logger.info(f"Copied {len(raw_paths)} images to {raw_dir}")
    return raw_paths

def compress_images(
    raw_paths: List[Path], 
    run_id: str, 
    config: PngquantConfig,
    obsidian_dir: Path
) -> CompressionSummary:
    """Compress images and return summary statistics."""
    run_dir = DATA_DIR / run_id
    raw_dir = run_dir / "raw"
    processed_dir = run_dir / "processed"
    failed_images = []

    # Save image paths
    save_image_paths(run_dir, raw_paths)

    # Process images
    for rel_path in tqdm(raw_paths, desc="Compressing images"):
        src = raw_dir / rel_path
        dst = processed_dir / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        if not src.exists():
            logger.warning(f"Missing file: {src}")
            failed_images.append(str(rel_path))
            continue

        # Build pngquant command
        cmd = ["pngquant"] + config.to_cli_args()
        
        # Add output path
        cmd.extend(["--output", str(dst)])
        
        # Add input file
        cmd.extend(["--", str(src)])
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"pngquant output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Compression failed for {src}: {e}")
            logger.error(f"Command output: {e.stdout}")
            logger.error(f"Command error: {e.stderr}")
            failed_images.append(str(rel_path))

    # Calculate statistics
    raw_size = sum(f.stat().st_size for f in raw_dir.rglob("*.png"))
    processed_size = sum(f.stat().st_size for f in processed_dir.rglob("*.png"))
    saved = raw_size - processed_size
    percent = (saved / raw_size * 100) if raw_size else 0

    # Create and save summary
    summary = CompressionSummary(
        run_id=run_id,
        timestamp=datetime.now().isoformat(),
        obsidian_dir=str(obsidian_dir),
        config=config,
        total_images=len(raw_paths),
        raw_size_bytes=raw_size,
        compressed_size_bytes=processed_size,
        space_saved_bytes=saved,
        space_saved_percent=percent,
        failed_images=failed_images
    )
    summary.save(run_dir)
    
    return summary

def report_compression(summary: CompressionSummary) -> None:
    """Print compression report from summary."""
    logger.info(f"Compression Summary for run {summary.run_id}")
    logger.info(f"Raw size: {summary.raw_size_bytes/1e6:.2f} MB")
    logger.info(f"Compressed size: {summary.compressed_size_bytes/1e6:.2f} MB")
    logger.info(f"Space saved: {summary.space_saved_bytes/1e6:.2f} MB ({summary.space_saved_percent:.1f}%)")
    if summary.failed_images:
        logger.warning(f"Failed to compress {len(summary.failed_images)} images")

def overwrite_originals(run_id: str) -> None:
    """Overwrite original images with compressed versions."""
    run_dir = DATA_DIR / run_id
    processed_dir = run_dir / "processed"
    
    with open(run_dir / "image_paths.txt") as f:
        rel_paths = [Path(line.strip()) for line in f]
    
    for rel_path in tqdm(rel_paths, desc="Overwriting originals"):
        src = processed_dir / rel_path
        dst = Path.cwd() / rel_path
        if src.exists():
            shutil.copy2(src, dst)
        else:
            logger.warning(f"Missing compressed file: {src}")

def undo_restore(run_id: str) -> None:
    """Restore original images from backup."""
    run_dir = DATA_DIR / run_id
    raw_dir = run_dir / "raw"
    
    with open(run_dir / "image_paths.txt") as f:
        rel_paths = [Path(line.strip()) for line in f]
    
    for rel_path in tqdm(rel_paths, desc="Restoring originals"):
        src = raw_dir / rel_path
        dst = Path.cwd() / rel_path
        if src.exists():
            shutil.copy2(src, dst)
        else:
            logger.warning(f"Missing backup file: {src}")

def cleanup_run(run_id: str) -> None:
    """Remove backup and processed files for a run."""
    run_dir = DATA_DIR / run_id
    if run_dir.exists():
        shutil.rmtree(run_dir)
        logger.info(f"Removed {run_dir}")
    else:
        logger.warning(f"No such run directory: {run_dir}") 