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

def sync_dotfiles():
    """Moves local configs to repo and replaces them with standard symlinks."""
    dotfiles = load_config()
    repo_root = os.path.dirname(os.path.abspath(__file__))

    for repo_name, sys_path in dotfiles.items():
        repo_dest_path = os.path.join(repo_root, repo_name)

        # Case 1: File is on the system but not in the repo yet
        if os.path.exists(sys_path) and not os.path.islink(sys_path) and not os.path.exists(repo_dest_path):
            print(f"📦 Tracking new dotfile: {sys_path}")
            shutil.move(sys_path, repo_dest_path)
            os.symlink(repo_dest_path, sys_path)
            print(f"🔗 Linked: {sys_path} -> {repo_dest_path}")
            
        # Case 2: File is already tracking correctly via symlink
        elif os.path.islink(sys_path):
            if os.readlink(sys_path) == repo_dest_path:
                print(f"✅ Already synced and healthy: {repo_name}")
            else:
                print(f"⚠️ Symlink mismatch for {repo_name}. Skipping to prevent data damage.")
        else:
            print(f"ℹ️ {repo_name} not yet active or setup on this machine. Run with --restore.")

def restore_dotfiles():
    """Deploys tracking data from the repository directly into a new environment."""
    dotfiles = load_config()
    repo_root = os.path.dirname(os.path.abspath(__file__))

    for repo_name, sys_path in dotfiles.items():
        repo_source_path = os.path.join(repo_root, repo_name)

        if not os.path.exists(repo_source_path):
            print(f"❌ Source tracking file missing in repo: {repo_name}. Skipping.")
            continue

        # Prevent overwriting actual unmanaged files without executing a backup first
        if os.path.exists(sys_path) and not os.path.islink(sys_path):
            backup_file(sys_path)
            os.remove(sys_path)
        elif os.path.islink(sys_path):
            os.remove(sys_path) # Safe to remove old/broken links

        # Ensure parent directories exist (e.g. ~/.config/path)
        parent_dir = os.path.dirname(sys_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        os.symlink(repo_source_path, sys_path)
        print(f"🚀 Restored and Linked: {sys_path} -> {repo_source_path}")

def main():
    parser = argparse.ArgumentParser(description="dotkeep: Minimalist dotfiles manager")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sync", action="store_true", help="Sync system config files into repo")
    group.add_argument("--restore", action="store_true", help="Deploy symlinks to system from repo storage")
    
    args = parser.parse_args()
    
    try:
        if args.sync:
            sync_dotfiles()
        elif args.restore:
            restore_dotfiles()
    except Exception as e:
        print(f"💥 Critical Failure: {e}")
