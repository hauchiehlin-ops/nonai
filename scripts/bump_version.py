#!/usr/bin/env python3
"""
NonAI Automated Version Bumper & Synchronizer
Automatically analyzes changes, bumps Semantic Version (major/minor/patch),
and synchronizes version tokens across pyproject.toml, version.json, __version__.py,
and UI HTML/JS entrypoints.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

VERSION_JSON_PATH = REPO_ROOT / "version.json"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
VERSION_PY_PATH = REPO_ROOT / "nonai" / "__version__.py"
INDEX_HTML_PATH = REPO_ROOT / "public" / "index.html"


def get_current_version() -> str:
    """Read current version from version.json, pyproject.toml, or fallback."""
    if VERSION_JSON_PATH.exists():
        try:
            with open(VERSION_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "version" in data:
                    return data["version"]
        except Exception:
            pass

    if PYPROJECT_PATH.exists():
        with open(PYPROJECT_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if m:
                return m.group(1)

    return "1.0.0"


def determine_bump_level_auto() -> str:
    """
    Intelligently inspect git diff and commit log to determine bump type:
    - 'major': breaking changes, complete re-architecture.
    - 'minor': new format support, forensic engine, package synthesis, feature modules.
    - 'patch': bug fixes, typo fixes, minor styling or parameter adjustments.
    """
    try:
        # Check git log of recent commits
        log_res = subprocess.run(
            ["git", "log", "-n", "5", "--pretty=format:%B"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        recent_msgs = log_res.stdout.lower()

        # Check git diff of staged + unstaged changes
        diff_res = subprocess.run(
            ["git", "diff", "HEAD~1"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        recent_diff = diff_res.stdout.lower()

        combined = recent_msgs + " " + recent_diff

        if "breaking change" in combined or "major overhaul" in combined:
            return "major"

        # Check for minor features
        minor_keywords = [
            "feat", "forensics", "synthesize", "de-pattern", "purge",
            "cross-format", "fonttable", "websettings", "theme1", "semantic",
            "new format", "pdf_sanitizer", "markdown_cleaner", "versioning"
        ]
        if any(k in combined for k in minor_keywords):
            return "minor"

        return "patch"
    except Exception:
        return "minor"


def bump_semver(current_ver: str, level: str) -> str:
    """Compute new semver string from current version and bump level."""
    m = re.match(r'^(\d+)\.(\d+)\.(\d+)', current_ver.strip().lstrip('v'))
    if not m:
        major, minor, patch = 1, 0, 0
    else:
        major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))

    if level == "major":
        major += 1
        minor = 0
        patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    elif level == "patch":
        patch += 1
    else:
        raise ValueError(f"Unknown bump level: {level}")

    return f"{major}.{minor}.{patch}"


def update_pyproject_toml(new_ver: str):
    if not PYPROJECT_PATH.exists():
        return
    with open(PYPROJECT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r'(version\s*=\s*["\'])[^"\']+(["\'])',
        rf'\g<1>{new_ver}\g<2>',
        content,
        count=1
    )
    with open(PYPROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [OK] Updated {PYPROJECT_PATH.relative_to(REPO_ROOT)} -> {new_ver}")


def update_version_py(new_ver: str):
    VERSION_PY_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = f'"""\nNonAI Version Specification\n"""\n__version__ = "{new_ver}"\n'
    with open(VERSION_PY_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Updated {VERSION_PY_PATH.relative_to(REPO_ROOT)} -> {new_ver}")


def update_version_json(new_ver: str, level: str, reason: str):
    data = {
        "version": new_ver,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "bump_level": level,
        "description": reason,
        "timestamp": datetime.now().isoformat()
    }
    with open(VERSION_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Updated {VERSION_JSON_PATH.relative_to(REPO_ROOT)} -> {new_ver}")


def update_html_badge(new_ver: str):
    badge_tag = f'<span id="appVersionBadge" class="version-badge" title="系統版本號">v{new_ver}</span>'
    targets = [INDEX_HTML_PATH, REPO_ROOT / "nonai" / "web" / "index.html"]

    for path in targets:
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        if 'id="appVersionBadge"' in html:
            new_html = re.sub(
                r'<span id="appVersionBadge"[^>]*>v?[^<]*</span>',
                badge_tag,
                html
            )
        else:
            new_html = html.replace(
                '<h1>NonAI</h1>',
                f'<div class="brand-title-wrap">\n            <h1>NonAI</h1>\n            {badge_tag}\n          </div>'
            )

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"  [OK] Updated {path.relative_to(REPO_ROOT)} badge -> v{new_ver}")


def main():
    parser = argparse.ArgumentParser(description="NonAI Automatic Version Bumper")
    parser.add_argument(
        "level",
        nargs="?",
        default="auto",
        choices=["auto", "patch", "minor", "major"],
        help="Semver bump level (default: auto)"
    )
    parser.add_argument(
        "--set",
        dest="set_version",
        default="",
        help="Explicitly set a specific semantic version (e.g. 1.1.0)"
    )
    parser.add_argument(
        "--reason",
        "-r",
        default="",
        help="Optional changelog description"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check and print current version without bumping"
    )

    args = parser.parse_args()

    curr_ver = get_current_version()

    if args.check:
        print(f"Current NonAI Version: v{curr_ver}")
        return

    if args.set_version:
        new_ver = args.set_version.lstrip("v")
        level = "manual"
    else:
        level = args.level
        if level == "auto":
            level = determine_bump_level_auto()
            print(f"Auto-detected bump level: [{level.upper()}] based on forensic & cross-format updates")
        new_ver = bump_semver(curr_ver, level)

    reason = args.reason or (
        "Cross-format forensic hardening (DOCX/PDF/MD/TXT), Claude Docs provenance eradication, "
        "Microsoft Word package synthesis, and neural transformer de-patterning."
    )

    print(f"\n=======================================================")
    print(f"  NonAI Version: v{curr_ver} -> v{new_ver} ({level.upper()})")
    print(f"  Reason: {reason}")
    print(f"=======================================================\n")

    update_version_json(new_ver, level, reason)
    update_pyproject_toml(new_ver)
    update_version_py(new_ver)
    update_html_badge(new_ver)

    print(f"\nVersion successfully set to v{new_ver}!\n")

if __name__ == "__main__":
    main()
