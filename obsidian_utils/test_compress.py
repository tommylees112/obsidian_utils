"""Test script to compress PNGs in a directory."""
from pathlib import Path
import shutil
from loguru import logger
from sys import path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
path.append(Path(__file__).parent.parent)

from obsidian_utils.config import PngquantConfig
from obsidian_utils.utils import compress_images, report_compression

def visualize_comparison(run_dir: Path, max_images: int = 4):
    """Create a grid visualization comparing raw and processed images.
    
    Args:
        run_dir: Path to the test run directory
        max_images: Maximum number of image pairs to display
    """
    raw_dir = run_dir / "raw"
    processed_dir = run_dir / "processed"
    
    # Get all PNG files
    raw_files = list(raw_dir.rglob("*.png"))
    if not raw_files:
        logger.warning("No images found to visualize")
        return
    
    # Limit the number of images to display
    raw_files = raw_files[:max_images]
    
    # Create figure with subplots
    n_images = len(raw_files)
    fig, axes = plt.subplots(n_images, 2, figsize=(10, 5*n_images))
    if n_images == 1:
        axes = axes.reshape(1, 2)  # Handle single image case
    
    # Plot each image pair
    for idx, raw_file in enumerate(raw_files):
        rel_path = raw_file.relative_to(raw_dir)
        processed_file = processed_dir / rel_path
        
        # Read images
        raw_img = mpimg.imread(raw_file)
        processed_img = mpimg.imread(processed_file)
        
        # Plot raw image
        axes[idx, 0].imshow(raw_img)
        axes[idx, 0].set_title(f"Raw: {raw_file.name}")
        axes[idx, 0].axis('off')
        
        # Plot processed image
        axes[idx, 1].imshow(processed_img)
        axes[idx, 1].set_title(f"Processed: {processed_file.name}")
        axes[idx, 1].axis('off')
    
    plt.tight_layout()
    plt.savefig(run_dir / "compression_comparison.png")
    logger.info(f"Saved visualization to {run_dir / 'compression_comparison.png'}")
    plt.close()

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
    
    # Verify directory structure and file existence
    run_dir = Path("data/test_run")
    raw_dir = run_dir / "raw"
    processed_dir = run_dir / "processed"
    
    # Check directories exist
    logger.info("Checking structure of directory")
    assert run_dir.exists(), f"Run directory {run_dir} does not exist"
    assert raw_dir.exists(), f"Raw directory {raw_dir} does not exist"
    assert processed_dir.exists(), f"Processed directory {processed_dir} does not exist"
    logger.success(f"Run Directory: {raw_dir} exists correctly")

    # Get all PNG files in raw directory
    logger.info("Checking for PNG files in raw directory")
    raw_files = list(raw_dir.rglob("*.png"))
    assert len(raw_files) > 0, "No PNG files found in raw directory"
    logger.success(f"Found {len(raw_files)} PNG files in raw directory")

    # Check each raw file has a corresponding processed file
    logger.info("Checking for processed files") 
    for raw_file in raw_files:
        rel_path = raw_file.relative_to(raw_dir)
        processed_file = processed_dir / rel_path
        assert processed_file.exists(), f"Processed file {processed_file} does not exist for raw file {raw_file}"
        assert processed_file.stat().st_size > 0, f"Processed file {processed_file} is empty"
    logger.success(f"Processed files exist correctly")

    # Create visualization
    visualize_comparison(run_dir)

    logger.info("All tests passed successfully!")
    
