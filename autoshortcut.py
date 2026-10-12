#!/usr/bin/env python3
import os
import glob
import shlex
import sys

# --- Parse arguments ---------------------------------------------------------
# Supports combined short flags (-do is the same as -d -o) and an optional
# positional path to any launchable file (e.g. a .sh script).
flags = set()
positional = []
for arg in sys.argv[1:]:
    if arg in ("-h", "--help"):
        flags.add("-h")
    elif arg.startswith("-") and len(arg) > 1:
        for ch in arg[1:]:
            flags.add("-" + ch)
    else:
        positional.append(arg)

make_desktop = "-d" in flags
remove_install = "-r" in flags
only_desktop = "-o" in flags
show_help = "-h" in flags
target_file = positional[0] if positional else None

if show_help:
    print("Usage: python autoshortcut.py [options] [file]")
    print()
    print("Install or remove a terminal command for the PyInstaller-built app in")
    print("dist/, or for any launchable file (e.g. a .sh script) given as an argument.")
    print()
    print("Options:")
    print("  [file]          Optional path to any launchable file (e.g. a .sh script,")
    print("                  AppImage, or binary). Shortcuts are created for that file")
    print("                  instead of the latest build in dist/. With -r, that file's")
    print("                  shortcuts are removed.")
    print("  No arguments    Normal install: create symlink in /usr/local/bin, and if")
    print("                  -d is also passed, create a .desktop file too.")
    print("  -d              Create a .desktop file in ~/.local/share/applications/")
    print("  -o              Only create the .desktop file, skip symlink creation")
    print("                  (only meaningful with -d)")
    print("  -r              Remove/uninstall mode: remove the symlink and .desktop file")
    print("  -h, --help      Show this help message and exit")
    print()
    print("Flags may be combined, e.g. -do is the same as -d -o.")
    sys.exit(0)

# 1️ Locate the latest build in dist/
workdir = None
if target_file:
    # Target is an explicitly given launchable file (e.g. a .sh script)
    exe_path = os.path.abspath(os.path.expanduser(target_file))
    if not os.path.isfile(exe_path):
        raise FileNotFoundError(f"File not found: {exe_path}")
    # Strip the extension for the shortcut name (foo.sh -> foo)
    exe_name = os.path.splitext(os.path.basename(exe_path))[0]
    workdir = os.path.dirname(exe_path)
    # Make sure the file is actually launchable
    if not os.access(exe_path, os.X_OK):
        os.chmod(exe_path, 0o755)
        print(f"Made file executable: {exe_path}")
else:
    dist_path = os.path.join(os.getcwd(), "dist")
    if not os.path.exists(dist_path):
        raise FileNotFoundError("dist/ folder not found. Run PyInstaller first.")

    subdirs = [d for d in glob.glob(os.path.join(dist_path, "*")) if os.path.isdir(d)]
    if not subdirs:
        raise FileNotFoundError("No build folders found in dist/")

    latest_build = max(subdirs, key=os.path.getmtime)
    exe_name = os.path.basename(latest_build)

# Paths used for install/removal
symlink_path = f"/usr/local/bin/{exe_name}"
desktop_path = os.path.expanduser(f"~/.local/share/applications/{exe_name}.desktop")

# --- REMOVE MODE (-r) ---
if remove_install:
    removed_anything = False

    if os.path.islink(symlink_path) or os.path.exists(symlink_path):
        print(f"Removing symlink: {symlink_path}")
        os.system(f"sudo rm {shlex.quote(symlink_path)}")
        removed_anything = True
    else:
        print("No symlink found.")

    if os.path.exists(desktop_path):
        print(f"Removing .desktop file: {desktop_path}")
        os.remove(desktop_path)
        removed_anything = True
    else:
        print("No .desktop file found.")

    if removed_anything:
        print("Removal complete.")
    else:
        print("Nothing to remove.")

    sys.exit(0)

# --- NORMAL INSTALL MODE ---

# Find the executable inside the build folder (dist/ mode only)
if target_file is None:
    files = [
        f for f in glob.glob(os.path.join(latest_build, "*"))
        if os.path.isfile(f) and not os.path.basename(f).startswith(".")
    ]

    if not files:
        raise FileNotFoundError(f"No executable found in {latest_build}")

    exe_path = os.path.abspath(files[0])

# 2 Create .desktop file only if -d is passed
if make_desktop:
    icon_path = "/usr/share/icons/gnome/32x32/status/network-transmit.png"
    # Quote the Exec value if the path contains spaces (per the desktop entry spec)
    exec_value = f'"{exe_path}"' if " " in exe_path else exe_path
    desktop_lines = [
        "[Desktop Entry]",
        f"Name={exe_name}",
        f"Comment=Run {exe_name}",
        f"Exec={exec_value}",
    ]
    if workdir:
        desktop_lines.append(f"Path={workdir}")
    desktop_lines += [
        f"Icon={icon_path}",
        "Terminal=false",
        "Type=Application",
        "Categories=Utility;",
    ]
    desktop_contents = "\n".join(desktop_lines) + "\n"

    if os.path.exists(desktop_path):
        response = input(
            f"A .desktop file for '{exe_name}' already exists. Overwrite? [y/N]: "
        ).strip().lower()
        if response != "y":
            print("Skipped .desktop creation.")
        else:
            with open(desktop_path, "w") as f:
                f.write(desktop_contents)
            os.chmod(desktop_path, 0o755)
            print(f".desktop file overwritten: {desktop_path}")
    else:
        with open(desktop_path, "w") as f:
            f.write(desktop_contents)
        os.chmod(desktop_path, 0o755)
        print(f".desktop file created: {desktop_path}")

# 3 Create symlink in /usr/local/bin (always unless -o is given)
if only_desktop:
    print("Skipping symlink creation (-o flag).")
elif os.path.exists(symlink_path):
    response = input(
        f"A file or command named '{exe_name}' already exists in /usr/local/bin. Overwrite? [y/N]: "
    ).strip().lower()
    if response != "y":
        print("Skipped creating symlink.")
    else:
        os.system(f"sudo rm {shlex.quote(symlink_path)}")
        os.system(f"sudo ln -s {shlex.quote(exe_path)} {shlex.quote(symlink_path)}")
        print(f"Symlink overwritten: {symlink_path} -> {exe_path}")
else:
    os.system(f"sudo ln -s {shlex.quote(exe_path)} {shlex.quote(symlink_path)}")
    print(f"Symlink created: {symlink_path} -> {exe_path}")

print(f"You can now run your app from the terminal: {exe_name}")
