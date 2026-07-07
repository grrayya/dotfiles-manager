import os
import shutil
import argparse
import json
from datetime import datetime

BACKUP_DIR = os.path.expanduser("~/.dotfiles_backup")

def backup_file(filepath):
    """Safely copies a file to a centralized backup folder before modifying it."""
    if not os.path.exists(filepath):
        return False
        
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"📁 Created backup directory at {BACKUP_DIR}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(filepath)
    backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}.bak")
    
    # Handle directories or regular files
    if os.path.isdir(filepath) and not os.path.islink(filepath):
        shutil.copytree(filepath, backup_path)
    elif os.path.isfile(filepath) and not os.path.islink(filepath):
        shutil.copy2(filepath, backup_path)
        
    print(f"💾 Backed up existing local file: {filepath} -> {backup_path}")
    return True

def load_config():
    """Loads and returns the config mapping file names to target paths."""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Missing config.json mapping file.")
        
    with open(config_path, "r") as f:
        config = json.load(f)
        
    # Expand ~ paths dynamically for the host operating system
    normalized_files = {}
    for repo_name, sys_path in config.get("dotfiles", {}).items():
        normalized_files[repo_name] = os.path.expanduser(sys_path)
        
    return normalized_files

def main():
    parser = argparse.ArgumentParser(description="dotkeep: Minimalist dotfiles manager")
    parser.add_argument("--sync", action="store_true", help="Sync system config files into repo")
    args = parser.parse_args()
    
    if args.sync:
        print("Syncing tracking logic coming next...")

if __name__ == "__main__":
    main()
