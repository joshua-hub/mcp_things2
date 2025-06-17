import json
import subprocess
import sys
from pathlib import Path
import re
import requests
from concurrent.futures import ThreadPoolExecutor

def get_latest_version(package):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json")
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
    except Exception as e:
        print(f"Error checking {package}: {e}")
    return "ERROR"

def parse_requirements(file_path):
    versions = {}
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Handle both requirements.txt and pyproject.toml formats
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' in line:
                        pkg, ver = line.split('==')
                        versions[pkg.strip()] = ver.strip()
                    elif '>=' in line:
                        pkg, ver = line.split('>=')
                        versions[pkg.strip()] = f">={ver.strip()}"
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return versions

def main():
    # Find all requirements.txt and pyproject.toml files
    files = []
    for pattern in ['**/requirements.txt', '**/pyproject.toml']:
        files.extend(Path('.').glob(pattern))
    
    all_packages = set()
    file_versions = {}
    
    # Collect all package versions
    for file_path in files:
        versions = parse_requirements(file_path)
        file_versions[str(file_path)] = versions
        all_packages.update(versions.keys())
    
    # Get latest versions using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        latest_versions = dict(zip(all_packages, executor.map(get_latest_version, all_packages)))
    
    # Print results
    print("\nPackage Version Analysis:")
    print("=" * 80)
    
    for file_path, versions in file_versions.items():
        print(f"\n{file_path}:")
        print("-" * 80)
        for pkg, ver in versions.items():
            latest = latest_versions.get(pkg, "ERROR")
            print(f"{pkg:20} Current: {ver:15} Latest: {latest:15}")

if __name__ == "__main__":
    main() 