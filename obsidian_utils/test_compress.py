"""Test script to compress PNGs in a directory."""
from pathlib import Path
import shutil
from loguru import logger
from sys import path
path.append(Path(__file__).parent.parent)

from obsidian_utils.config import PngquantConfig
from obsidian_utils.utils import compress_images, report_compression

def test_compress_directory(input_dir: str = "data/raw", output_dir: str = "data/processed"):
    """Test compression on a directory of PNGs."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create all necessary directories
    run_dir = Path("data/test_run")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw").mkdir(exist_ok=True)
    (run_dir / "processed").mkdir(exist_ok=True)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all PNG files
    png_files = list(input_path.rglob("*.png"))
    logger.info(f"Found {len(png_files)} PNG files in {input_dir}")
    
    if not png_files:
        logger.error("No PNG files found!")
        return
    
    # Copy files to test_run/raw
    for png_file in png_files:
        rel_path = png_file.relative_to(input_path)
        dest_path = run_dir / "raw" / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png_file, dest_path)
        logger.info(f"Copied {png_file} to {dest_path}")
    
    # Create config
    config = PngquantConfig(
        quality_min=65,
        quality_max=80,
        speed=1
    )
    
    # Convert to relative paths
    rel_paths = [p.relative_to(input_path) for p in png_files]
    
    # Run compression
    summary = compress_images(
        raw_paths=rel_paths,
        run_id="test_run",
        config=config,
        obsidian_dir=input_path
    )
    
    # Report results
    report_compression(summary)

if __name__ == "__main__":
    # Configure logger
    logger.add("test_compress.log", rotation="1 MB")
    
    # Run test
    test_compress_directory() 