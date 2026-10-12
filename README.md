# Autoshortcut

Simple Python script to create terminal shortcuts and .desktop files for PyInstaller-built executables — or for any launchable file, such as a `.sh` script. Makes it easy to run Python apps and other programs from the terminal or GNOME Activities overview.

## Workflow

1. Create your Python app
2. Run `pyinstaller app_name.py` to build it
3. Run `python autoshortcut.py [options]` to install it

Autoshortcut automatically finds the latest build in the `dist/` directory and creates the necessary symlinks and desktop files.

You can also point it at any launchable file (e.g. a `.sh` script) to create shortcuts for that instead:

```bash
python autoshortcut.py -d -o /path/to/something.sh
```

## Usage

```
python autoshortcut.py [options] [file]
```

### Options

- **`[file]`**: Optional path to any launchable file (e.g. a `.sh` script, AppImage, or binary)
  - Shortcuts are created for that file instead of the latest build in `dist/`
  - The file is made executable if it isn't already
  - The shortcut name comes from the file name without its extension (`something.sh` -> `something`)
  - The created `.desktop` file includes a `Path=` entry pointing at the file's folder
  - Can also be combined with `-r` to remove that file's shortcuts

- **No arguments**: Normal install mode (latest build in `dist/`)
  - Creates a symlink in `/usr/local/bin/` for terminal access
  - If `-d` is also passed, creates a .desktop file for the Activities menu

- **`-d`**: Create a .desktop file
  - Generates a .desktop entry in `~/.local/share/applications/`
  - Can be combined with default install or used with `-o` to create only the desktop file
  - Prompts before overwriting existing files

- **`-o`**: Desktop file only
  - Creates only the .desktop file, skips symlink creation
  - Only meaningful when combined with `-d`

- **`-r`**: Remove/uninstall mode
  - Removes the symlink from `/usr/local/bin/`
  - Removes the .desktop file if it exists

- **`-h`, `--help`**: Show help message and exit

Flags may be combined: `-do` is the same as `-d -o`.

## Examples

```bash
# Normal install: create symlink in /usr/local/bin
python autoshortcut.py

# Create symlink and .desktop file
python autoshortcut.py -d

# Create only .desktop file (no terminal access)
python autoshortcut.py -d -o

# Create only a .desktop file for any launchable file, e.g. a shell script
python autoshortcut.py -do /path/to/game.sh

# Remove the app installation
python autoshortcut.py -r

# Remove the shortcuts created for a specific file
python autoshortcut.py -r /path/to/game.sh

# Show help
python autoshortcut.py --help
```

## After Installation

Once installed, you can run your app from the terminal using the executable name:
```bash
app_name
```

If you created a .desktop file with `-d`, the app will also appear in your Activities menu.