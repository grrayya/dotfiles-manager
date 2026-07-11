import os
import shutil
import argparse
import json
from datetime import datetime

BACKUP_DIR = os.path.expanduser("~/.dotfiles_backup")


def backup_file(filepath):
    """Copy filepath into BACKUP_DIR with a timestamp suffix.
    Symlinks are skipped -- only real files/dirs get backed up, since
    backing up a link would just copy the link itself, not the content.
    """
    if not os.path.exists(filepath):
        return False

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Created backup directory at {BACKUP_DIR}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(filepath)
    backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}.bak")

    if os.path.isdir(filepath) and not os.path.islink(filepath):
        shutil.copytree(filepath, backup_path)
    elif os.path.isfile(filepath) and not os.path.islink(filepath):
        shutil.copy2(filepath, backup_path)

    print(f"Backed up: {filepath} -> {backup_path}")
    return True


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError("Missing config.json mapping file.")

    with open(config_path, "r") as f:
        config = json.load(f)

    dotfiles = config.get("dotfiles", {})
    if not dotfiles:
        raise ValueError("config.json has no entries under \"dotfiles\".")


    return {
        repo_name: os.path.expanduser(sys_path)
        for repo_name, sys_path in dotfiles.items()
    }


def status_dotfiles():
    """Report how each tracked dotfile currently stands, without touching anything."""
    dotfiles = load_config()
    repo_root = os.path.dirname(os.path.abspath(__file__))

    for repo_name, sys_path in dotfiles.items():
        repo_dest_path = os.path.join(repo_root, repo_name)
        in_repo = os.path.exists(repo_dest_path)

        if os.path.islink(sys_path):
            if os.readlink(sys_path) == repo_dest_path:
                print(f"[linked]    {repo_name}")
            else:
                print(f"[mismatch]  {repo_name} -> points elsewhere ({os.readlink(sys_path)})")
        elif os.path.exists(sys_path) and in_repo:
            print(f"[conflict]  {repo_name} -> exists both on system and in repo, unlinked")
        elif os.path.exists(sys_path) and not in_repo:
            print(f"[untracked] {repo_name} -> on system, not yet in repo (run --sync)")
        elif in_repo and not os.path.exists(sys_path):
            print(f"[repo-only] {repo_name} -> in repo, missing on system (run --restore)")
        else:
            print(f"[missing]   {repo_name} -> not found on system or in repo")


def sync_dotfiles(dry_run=False):
    dotfiles = load_config()
    repo_root = os.path.dirname(os.path.abspath(__file__))

    for repo_name, sys_path in dotfiles.items():
        repo_dest_path = os.path.join(repo_root, repo_name)
        repo_dest_parent = os.path.dirname(repo_dest_path)

        if os.path.islink(sys_path):
            if os.readlink(sys_path) == repo_dest_path:
                print(f"Already synced: {repo_name}")
            else:
                # Don't touch a symlink that points somewhere we don't expect --
                # could be a manual setup we'd break by overwriting it
                print(f"Symlink mismatch for {repo_name}, skipping to avoid clobbering it.")
            continue

        if not os.path.exists(sys_path):
            print(f"{repo_name} not set up on this machine yet. Run with --restore.")
            continue

        if os.path.exists(repo_dest_path):
            print(f"Conflict: {repo_name} exists both on system and in repo but isn't linked. "
                  f"Resolve by hand (compare {sys_path} vs {repo_dest_path}), then re-run --sync.")
            continue

        print(f"Tracking new dotfile: {sys_path}")
        if dry_run:
            print(f"  (dry-run) would move {sys_path} -> {repo_dest_path} and symlink it back")
            continue

        if repo_dest_parent and not os.path.exists(repo_dest_parent):
            os.makedirs(repo_dest_parent)

        shutil.move(sys_path, repo_dest_path)
        os.symlink(repo_dest_path, sys_path)
        print(f"Linked: {sys_path} -> {repo_dest_path}")


def restore_dotfiles(dry_run=False):
    dotfiles = load_config()
    repo_root = os.path.dirname(os.path.abspath(__file__))

    for repo_name, sys_path in dotfiles.items():
        repo_source_path = os.path.join(repo_root, repo_name)

        if not os.path.exists(repo_source_path):
            print(f"Missing from repo, skipping: {repo_name}")
            continue

        if dry_run:
            action = "back up + replace" if os.path.exists(sys_path) and not os.path.islink(sys_path) else "link"
            print(f"(dry-run) would {action}: {sys_path} -> {repo_source_path}")
            continue

        if os.path.exists(sys_path) and not os.path.islink(sys_path):
            backup_file(sys_path)
            os.remove(sys_path)
        elif os.path.islink(sys_path):
            os.remove(sys_path)

        parent_dir = os.path.dirname(sys_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        os.symlink(repo_source_path, sys_path)
        print(f"Restored: {sys_path} -> {repo_source_path}")


def main():
    parser = argparse.ArgumentParser(description="dotkeep: minimalist dotfiles manager")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sync", action="store_true", help="Sync system config files into repo")
    group.add_argument("--restore", action="store_true", help="Deploy symlinks to system from repo storage")
    group.add_argument("--status", action="store_true", help="Show sync state without changing anything")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without touching the filesystem")

    args = parser.parse_args()

    try:
        if args.sync:
            sync_dotfiles(dry_run=args.dry_run)
        elif args.restore:
            restore_dotfiles(dry_run=args.dry_run)
        elif args.status:
            status_dotfiles()
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError as e:
        print(f"Permission denied: {e}")
    except ValueError as e:
        print(f"Config error: {e}")


if __name__ == "__main__":
    main()
