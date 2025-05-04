import pytest
import importlib


@pytest.mark.parametrize("package_name", [
    "fastapi",
    "pydantic",
    "dotenv",
    "pyodbc",
    "uvicorn"
])
def test_required_packages_installed(package_name):
    """
    Test that all required packages are installed.
    
    This test verifies that the basic required packages can be imported,
    which means they are correctly installed.
    """
    # Map package name to import name if different
    import_map = {
        "dotenv": "python-dotenv"
    }
    
    try:
        # Use the mapped name if it exists, otherwise use the package name
        import_name = import_map.get(package_name, package_name)
        module = importlib.import_module(import_name)
        assert module is not None
    except ImportError as e:
        pytest.fail(f"Required package '{package_name}' is not installed: {e}")


def test_optional_packages():
    """
    Test for optional packages and provide information if they're missing.
    """
    optional_packages = [
        "anthropic",
        "mcp"
    ]
    
    for package in optional_packages:
        try:
            module = importlib.import_module(package)
            print(f"Optional package '{package}' is installed")
        except ImportError:
            print(f"Optional package '{package}' is not installed (not required)")
