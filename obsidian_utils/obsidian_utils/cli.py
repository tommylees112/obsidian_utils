"""Command-line interface for image compression."""
import click
from pathlib import Path

from loguru import logger

from .config import PngquantConfig
from .utils import (
    generate_run_id,
    scan_and_copy_images,
    compress_images,
    report_compression,
    overwrite_originals,
    undo_restore,
    cleanup_run,
)

@click.group()
def cli():
    """Compress PNG images in your Obsidian vault."""
    pass

@cli.command()
@click.option('--obsidian-dir', type=click.Path(exists=True, file_okay=False), required=True)
@click.option('--quality-min', default=65, show_default=True)
@click.option('--quality-max', default=80, show_default=True)
@click.option('--speed', default=1, show_default=True)
@click.option('--run-id', default=None)
def run(
    obsidian_dir: str, 
    quality_min: int, 
    quality_max: int, 
    speed: int, 
    run_id: str | None
) -> None:
    """Scan, backup, and compress images."""
    obsidian_path = Path(obsidian_dir)
    run_id = run_id or generate_run_id()
    logger.info(f"Run ID: {run_id}")

    config = PngquantConfig(
        quality_min=quality_min,
        quality_max=quality_max,
        speed=speed
    )

    raw_paths = scan_and_copy_images(obsidian_path, run_id)
    summary = compress_images(raw_paths, run_id, config, obsidian_path)
    report_compression(summary)

@cli.command()
@click.option('--run-id', required=True)
def overwrite(run_id: str) -> None:
    """Overwrite originals with compressed images."""
    overwrite_originals(run_id)

@cli.command()
@click.option('--run-id', required=True)
def undo(run_id: str) -> None:
    """Restore originals from backup."""
    undo_restore(run_id)

@cli.command()
@click.option('--run-id', required=True)
def cleanup(run_id: str) -> None:
    """Remove backup and processed files for a run."""
    cleanup_run(run_id)

if __name__ == '__main__':
    cli() 