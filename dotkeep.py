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

def main():
    parser = argparse.ArgumentParser(description="dotkeep: Minimalist dotfiles manager")
    parser.add_argument("--sync", action="store_true", help="Sync system config files into repo")
    args = parser.parse_args()
    
    if args.sync:
        print("Syncing tracking logic coming next...")

if __name__ == "__main__":
    main()
