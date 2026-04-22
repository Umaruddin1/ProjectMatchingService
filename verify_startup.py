#!/usr/bin/env python
"""
Startup verification script for Accounting Reconciliation Service.

This script verifies all dependencies, imports, and configurations
before starting the FastAPI server.
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python 3.11+ required, found {version.major}.{version.minor}")
        return False


def check_dependencies():
    """Check if all required dependencies are installed."""
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "openpyxl",
        "fuzzywuzzy",
        "pytest",
    ]
    
    missing = []
    for package in required:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    return len(missing) == 0


def check_modules():
    """Check if all project modules can be imported."""
    sys.path.insert(0, str(Path(__file__).parent))
    
    modules = [
        "app.main",
        "app.api.v1.endpoints.process",
        "app.api.v1.endpoints.reconcile",
        "app.api.v1.endpoints.export",
        "app.services.file_validation_service",
        "app.services.excel_parser_service",
        "app.services.normalization_service",
        "app.services.matching_service",
        "app.services.reconciliation_service",
        "app.services.export_service",
        "app.core.config",
        "app.core.exceptions",
    ]
    
    failed = []
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name}")
        except Exception as e:
            print(f"✗ {module_name} - {e}")
            failed.append(module_name)
    
    return len(failed) == 0


def check_routes():
    """Check if all API routes are registered."""
    sys.path.insert(0, str(Path(__file__).parent))
    
    from app.main import app
    
    required_routes = {
        "/": "GET",
        "/health": "GET",
        "/api/v1/process": "POST",
        "/api/v1/reconcile": "POST",
        "/api/v1/export": "POST",
    }
    
    found_routes = {}
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            found_routes[route.path] = route.methods
    
    missing = []
    for path, method in required_routes.items():
        if path in found_routes and method in found_routes[path]:
            print(f"✓ {method} {path}")
        else:
            print(f"✗ {method} {path}")
            missing.append(f"{method} {path}")
    
    return len(missing) == 0


def main():
    """Run all startup checks."""
    print("=" * 60)
    print("Accounting Reconciliation Service - Startup Verification")
    print("=" * 60)
    
    print("\n1. Python Version")
    if not check_python_version():
        sys.exit(1)
    
    print("\n2. Dependencies")
    if not check_dependencies():
        print("\nInstall missing dependencies with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n3. Project Modules")
    if not check_modules():
        sys.exit(1)
    
    print("\n4. API Routes")
    if not check_routes():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ All checks passed! Ready to start.")
    print("=" * 60)
    print("\nStart server with:")
    print("  python -m uvicorn app.main:app --reload")
    print("\nThen access:")
    print("  - API docs: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
