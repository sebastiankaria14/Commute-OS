#!/usr/bin/env python3
"""
Setup script for CommuteOS development environment.
Run this script to verify dependencies and setup.
"""
import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_docker():
    """Check if Docker is installed"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found. Please install Docker Desktop.")
        return False


def check_docker_compose():
    """Check if Docker Compose is installed"""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose not found.")
        return False


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
        return True
    else:
        print("❌ .env.example not found")
        return False


def check_project_structure():
    """Verify project structure"""
    required_dirs = [
        "commuteos/services/api_gateway",
        "commuteos/services/routing_service",
        "commuteos/shared/config",
        "commuteos/shared/database",
        "commuteos/shared/cache",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} not found")
            all_exist = False
    
    return all_exist


def main():
    """Main setup verification"""
    print("=" * 60)
    print("CommuteOS Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Docker", check_docker),
        ("Docker Compose", check_docker_compose),
        ("Environment File", create_env_file),
        ("Project Structure", check_project_structure),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed! You're ready to go.")
        print("\nNext steps:")
        print("  1. docker-compose up -d")
        print("  2. Visit http://localhost:8000/health")
        print("  3. Check README.md for API documentation")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
