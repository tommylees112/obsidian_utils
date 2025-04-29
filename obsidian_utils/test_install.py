"""Test script to verify installation."""
import subprocess
import sys

def test_installation():
    """Test if the package is installed correctly."""
    try:
        # Test Python version
        print(f"Python version: {sys.version}")
        
        # Test pngquant installation
        result = subprocess.run(
            ["pngquant", "--version"],
            capture_output=True,
            text=True
        )
        print(f"pngquant version: {result.stdout.strip()}")
        
        # Test package installation
        import obsidian_utils
        print(f"obsidian_utils version: {obsidian_utils.__version__}")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_installation() 