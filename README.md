# Dotfiles Manager

tool that helps to manage, monitor, and deploy your configuration files (dotfiles).

## Features

The `dotkeep` tool consolidates your different system configuration files (e.g., `.bashrc`, `.vimrc`, or your CLI tools' configuration files) into one repository. The process occurs in both ways:
1. **Synchronization:** Places your current system config files in your repository and creates symlinks of them.
2. **Deployment:** Deploys your monitored dotfiles from your repository to your new machine by generating symlinks.

**Key Features:**
* **Zero Dependencies:** The `dotkeep` tool works purely on Python's Standard Library.
* **Safe Backups:** Safely backs up your local files in the `~/.dotfiles_backup` folder before overwriting/symlinking them.
* **JSON Mapping:** Uses simple and clear `config.json` file to map your repository files to system files paths.

---

## Setup and Configuration

As the `dotkeep` tool is dependent on nothing else but Python's Standard Library, there is no need for additional installations. But you have to specify which files you want to manage through the tool via `config.json`.

1. Create a file `dotkeep.py` inside your dotfiles repository.
2. Create `config.json` file in the very same folder.
3. Map file names of your repo to system files locations.
