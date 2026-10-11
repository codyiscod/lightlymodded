import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
VERSION_DIR = SCRIPT_DIR / "versions"

# loop through each version
for version_file in VERSION_DIR.iterdir():
    if version_file.is_file():
        # get version
        version = version_file.name.strip(".json")
        print(version)

