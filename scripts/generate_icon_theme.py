#!/usr/bin/env python3
"""Generate the Zed icon theme from the material-icon-theme npm package.

Downloads the pinned version of https://www.npmjs.com/package/material-icon-theme
(the built distribution of material-extensions/vscode-material-icon-theme),
converts its mappings to Zed's icon theme schema, and writes:

  - icon_themes/material-icons.json  (dark + light themes)
  - icons/material/*.svg        (only the SVGs actually referenced)
  - licenses/material-icon-theme.LICENSE

The official Pkl logo in icons/pkl.svg is kept for Pkl files, overriding the
material `pkl` icon.

Conversion notes (why this isn't a 1:1 copy):

  - VS Code lowercases file names before matching; Zed matches case-sensitively.
    For all-lowercase file-name keys we also emit `Capitalized` and `UPPERCASE`
    variants (e.g. `makefile` -> `Makefile`, `readme.md` -> `README.md`) so the
    common on-disk spellings still match.
  - Keys containing `/` (VS Code path patterns like `.config/graphqlrc`) are
    dropped; Zed only matches against the file name.
  - VS Code `languageIds` mappings have no Zed equivalent and are dropped.

Usage:
    python3 scripts/generate_icon_theme.py [--package-dir DIR]

With --package-dir, uses an already-extracted npm package instead of
downloading (the directory containing package.json, dist/, icons/).
"""

import argparse
import io
import json
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

UPSTREAM_VERSION = "5.36.1"
TARBALL_URL = (
    "https://registry.npmjs.org/material-icon-theme/-/"
    f"material-icon-theme-{UPSTREAM_VERSION}.tgz"
)

REPO_ROOT = Path(__file__).resolve().parent.parent

FAMILY_NAME = "Material Icons"
AUTHOR = "Eduardo Aguilar"
SCHEMA = "https://zed.dev/schema/icon_themes/v0.3.0.json"


def download_package(dest: Path) -> Path:
    print(f"Downloading material-icon-theme {UPSTREAM_VERSION}...")
    with urllib.request.urlopen(TARBALL_URL) as resp:
        data = resp.read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        tar.extractall(dest, filter="data")
    return dest / "package"


def casing_variants(name: str) -> list[str]:
    """Extra spellings to emit for an all-lowercase file-name key."""
    if name != name.lower() or not name or not name[0].isalpha():
        return []
    stem, dot, suffix = name.partition(".")
    variants = {
        name[0].upper() + name[1:],          # makefile -> Makefile
        stem.upper() + dot + suffix,          # readme.md -> README.md
    }
    variants.discard(name)
    return sorted(variants)


def build_theme(data: dict, appearance: str) -> tuple[dict, set[str]]:
    """Build one Zed theme dict; returns (theme, referenced icon names)."""
    defs = data["iconDefinitions"]

    file_suffixes = dict(data["fileExtensions"])
    file_stems = {}
    for key, icon in data["fileNames"].items():
        if "/" in key:
            continue
        file_stems[key] = icon
        for variant in casing_variants(key):
            file_stems.setdefault(variant, icon)

    folder_names = dict(data["folderNames"])
    folder_names_expanded = dict(data["folderNamesExpanded"])

    if appearance == "light":
        light = data["light"]
        file_suffixes.update(light["fileExtensions"])
        for key, icon in light["fileNames"].items():
            if "/" in key:
                continue
            file_stems[key] = icon
            for variant in casing_variants(key):
                file_stems[variant] = icon
        folder_names.update(light["folderNames"])
        folder_names_expanded.update(light["folderNamesExpanded"])

    def icon_path(name: str) -> str:
        svg = Path(defs[name]["iconPath"]).name
        return f"./icons/material/{svg}"

    file_icons = {
        icon: {"path": icon_path(icon)}
        for icon in sorted(set(file_suffixes.values()) | set(file_stems.values()))
    }
    file_icons["default"] = {"path": icon_path(data["file"])}

    # Pkl files keep the official logo (see README attribution).
    file_suffixes["pkl"] = "pkl"
    file_suffixes["pcf"] = "pkl"
    file_stems["PklProject"] = "pkl"
    file_icons["pkl"] = {"path": "./icons/pkl.svg"}

    # EJSON files are encrypted JSON; reuse the JSON icon (upstream has no ejson).
    file_suffixes["ejson"] = "json"

    named_directory_icons = {
        name: {
            "collapsed": icon_path(folder_names[name]),
            "expanded": icon_path(folder_names_expanded[name]),
        }
        for name in sorted(folder_names)
        if "/" not in name and name in folder_names_expanded
    }

    theme = {
        "name": FAMILY_NAME if appearance == "dark" else f"{FAMILY_NAME} Light",
        "appearance": appearance,
        "directory_icons": {
            "collapsed": icon_path(data["folder"]),
            "expanded": icon_path(data["folderExpanded"]),
        },
        "named_directory_icons": named_directory_icons,
        "file_stems": dict(sorted(file_stems.items())),
        "file_suffixes": dict(sorted(file_suffixes.items())),
        "file_icons": dict(sorted(file_icons.items())),
    }

    referenced = set(file_suffixes.values()) | set(file_stems.values())
    referenced.discard("pkl")
    referenced |= set(folder_names.values()) | set(folder_names_expanded.values())
    referenced |= {data["file"], data["folder"], data["folderExpanded"]}
    return theme, referenced


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, default=None)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        pkg = args.package_dir or download_package(Path(tmp))
        data = json.loads((pkg / "dist" / "material-icons.json").read_text())

        dark, refs_dark = build_theme(data, "dark")
        light, refs_light = build_theme(data, "light")

        family = {
            "$schema": SCHEMA,
            "name": FAMILY_NAME,
            "author": AUTHOR,
            "themes": [dark, light],
        }
        theme_path = REPO_ROOT / "icon_themes" / "material-icons.json"
        theme_path.write_text(json.dumps(family, indent=2) + "\n")

        icons_dir = REPO_ROOT / "icons" / "material"
        if icons_dir.exists():
            shutil.rmtree(icons_dir)
        icons_dir.mkdir(parents=True)
        for icon in sorted(refs_dark | refs_light):
            svg = Path(data["iconDefinitions"][icon]["iconPath"]).name
            shutil.copyfile(pkg / "icons" / svg, icons_dir / svg)

        licenses_dir = REPO_ROOT / "licenses"
        licenses_dir.mkdir(exist_ok=True)
        shutil.copyfile(pkg / "LICENSE", licenses_dir / "material-icon-theme.LICENSE")

        print(f"Wrote {theme_path.relative_to(REPO_ROOT)}")
        print(f"Copied {len(list(icons_dir.glob('*.svg')))} SVGs to icons/material/")
        print(
            f"Themes: {dark['name']} ({len(dark['file_suffixes'])} suffixes, "
            f"{len(dark['file_stems'])} stems, "
            f"{len(dark['named_directory_icons'])} folders)"
        )


if __name__ == "__main__":
    main()
