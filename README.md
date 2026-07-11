# Dotfiles Manager

A small tool for managing dotfiles across machines without pulling in any dependencies.

`dotkeep` keeps your config files (`.bashrc`, `.vimrc`, whatever else you track) in one repo instead of scattered around. 


## Features

- **No dependencies** — everything runs on Python's standard library, nothing to `pip install`.
- **Backups before it touches anything** — your existing files get copied to `~/.dotfiles_backup` before dotkeep overwrites or symlinks them.
- **Plain JSON mapping** — `config.json` maps repo files to their destination paths, so there's no magic about where things end up.

## Setup

1. Drop `dotkeep.py` into your dotfiles repo.
2. Add a `config.json` next to it, mapping repo filenames to system paths. For example:

```json
{
  "bashrc": "~/.bashrc",
  "vimrc": "~/.vimrc"
}
```

<!-- Replace this with your actual config.json format if it's different -->

3. Run it. That's it — no installation step, since it's pure standard library.
