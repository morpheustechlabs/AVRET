#!/usr/bin/env python3
"""
AVRET Public GitHub Release Manager

Public distribution only. This script does not publish AVRET application source code.

Expected layout:

.../OSX_FinalBuild_Distributions/AVRET/
├── AVRET-GIT-Public/          <- this public Git repository
│   ├── release/
│   └── scripts/
│       └── avret_git_release.py
├── dist1.1.6_b26081203/
│   ├── AVRET-1.1.6-b26081203.dmg
│   └── AVRET-1.1.6-b26081203.sha256
└── ...

GitHub repository:
    git@morpheustechlabs-GitHub:morpheustechlabs/AVRET.git
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

GITHUB_REPO = "morpheustechlabs/AVRET"
SSH_REMOTE = "git@morpheustechlabs-GitHub:morpheustechlabs/AVRET.git"
MAX_GITHUB_BLOB = 100 * 1024 * 1024  # GitHub's normal Git blob limit.

DIST_RE = re.compile(r"^dist(?P<version>\d+\.\d+\.\d+)_b(?P<build>\d+)$")
DMG_RE = re.compile(r"^AVRET-(?P<version>\d+\.\d+\.\d+)-b(?P<build>\d+)\.dmg$")


@dataclass(frozen=True)
class Build:
    version: str
    build: str
    dist_dir: Path
    dmg: Path

    @property
    def tag(self) -> str:
        return f"v{self.version}"

    @property
    def dmg_name(self) -> str:
        return self.dmg.name

    @property
    def sha_name(self) -> str:
        return f"{self.dmg.name}.sha256"

    @property
    def title(self) -> str:
        return f"AVRET {self.version} — macOS Universal"


def run(cmd, *, cwd=None, check=True, capture=False):
    print("+", " ".join(str(x) for x in cmd))
    return subprocess.run(
        [str(x) for x in cmd],
        cwd=cwd,
        check=check,
        text=True,
        capture_output=capture,
    )


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def dist_root() -> Path:
    return repo_root().parent


def version_key(version: str):
    return tuple(int(x) for x in version.split("."))


def find_builds():
    root = dist_root()
    builds = []
    for p in root.iterdir():
        if not p.is_dir():
            continue
        m = DIST_RE.match(p.name)
        if not m:
            continue
        version = m.group("version")
        build = m.group("build")
        expected = p / f"AVRET-{version}-b{build}.dmg"
        if expected.is_file():
            builds.append(Build(version, build, p, expected))
    return sorted(builds, key=lambda b: (version_key(b.version), int(b.build)), reverse=True)


def choose_build():
    builds = find_builds()
    if not builds:
        raise SystemExit(f"No AVRET dist build containing a DMG was found under:\n  {dist_root()}")

    print("\nAvailable AVRET distributions:\n")
    for i, b in enumerate(builds, 1):
        marker = "  <-- newest" if i == 1 else ""
        print(f"  {i}. AVRET {b.version}  build {b.build}{marker}")
        print(f"     {b.dmg}")

    print()
    answer = input("Select build [1]: ").strip()
    idx = 1 if not answer else int(answer)
    if idx < 1 or idx > len(builds):
        raise SystemExit("Invalid selection.")
    return builds[idx - 1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_expected_sha(build: Build):
    candidates = [
        build.dist_dir / build.sha_name,
        build.dist_dir / f"AVRET-{build.version}-b{build.build}.sha256",
    ]
    for p in candidates:
        if p.is_file():
            line = p.read_text(errors="replace").strip().splitlines()[0]
            token = line.split()[0]
            if re.fullmatch(r"[0-9a-fA-F]{64}", token):
                return token.lower(), p
    return None, None


def verify(build: Build):
    print("\n=== VERIFY ===")
    actual = sha256(build.dmg)
    expected, sha_file = read_expected_sha(build)

    print(f"DMG:      {build.dmg}")
    print(f"SHA-256:  {actual}")

    if expected:
        if actual != expected:
            raise SystemExit(
                "\nERROR: SHA-256 mismatch.\n"
                f"Expected: {expected}\n"
                f"Actual:   {actual}"
            )
        print(f"Checksum verified against: {sha_file}")
    else:
        print("No existing checksum file found; a fresh checksum will be generated.")

    xcrun = shutil.which("xcrun")
    if xcrun:
        print("\nChecking Apple stapled notarization ticket...")
        run([xcrun, "stapler", "validate", str(build.dmg)])
    else:
        print("\nWARNING: xcrun not found; notarization ticket was not validated.")

    return actual


def ensure_git_repo():
    root = repo_root()
    if not (root / ".git").exists():
        print("\nInitializing Git repository...")
        run(["git", "init", "-b", "main"], cwd=root)

    # Always force this repository to the Morpheus SSH identity, never HTTPS.
    remotes = run(["git", "remote"], cwd=root, capture=True).stdout.split()
    if "origin" in remotes:
        run(["git", "remote", "set-url", "origin", SSH_REMOTE], cwd=root)
    else:
        run(["git", "remote", "add", "origin", SSH_REMOTE], cwd=root)

    remote = run(["git", "remote", "get-url", "origin"], cwd=root, capture=True).stdout.strip()
    if remote != SSH_REMOTE:
        raise SystemExit(f"ERROR: origin is not the Morpheus SSH remote:\n  {remote}")

    print(f"Git origin: {remote}")


def github_blob_strategy(build: Build):
    size = build.dmg.stat().st_size
    print(f"\nDMG size: {size / (1024*1024):.1f} MiB")

    if size <= MAX_GITHUB_BLOB:
        return "normal"

    if shutil.which("git-lfs"):
        print("DMG exceeds GitHub's normal 100 MiB Git blob limit.")
        print("git-lfs is installed; the DMG will be tracked with Git LFS.")
        return "lfs"

    raise SystemExit(
        "\nERROR: The DMG exceeds GitHub's normal 100 MiB file limit and git-lfs is not installed.\n"
        "Install it with:\n"
        "  brew install git-lfs\n"
        "  git lfs install\n"
        "Then rerun this program."
    )


def remove_old_release_payloads(release_dir: Path, keep_names):
    for p in release_dir.iterdir():
        if p.name in keep_names:
            continue
        if p.is_symlink() and p.name.startswith("AVRET-"):
            p.unlink()
        elif p.is_file() and (
            p.name.endswith(".dmg")
            or p.name.endswith(".dmg.sha256")
            or p.name in ("AVRET-latest.sha256",)
        ):
            p.unlink()


def stage_release(build: Build, actual_sha: str, blob_strategy: str):
    root = repo_root()
    release_dir = root / "release"
    release_dir.mkdir(exist_ok=True)

    immutable_dmg = release_dir / build.dmg_name
    immutable_sha = release_dir / build.sha_name
    latest_link = release_dir / "AVRET-latest.dmg"
    latest_sha_link = release_dir / "AVRET-latest.sha256"
    notes = release_dir / f"RELEASE-NOTES-v{build.version}.md"

    keep = {
        immutable_dmg.name,
        immutable_sha.name,
        latest_link.name,
        latest_sha_link.name,
        notes.name,
    }
    remove_old_release_payloads(release_dir, keep)

    print("\n=== STAGE PUBLIC RELEASE ===")
    print(f"Copying actual DMG into Git repo:\n  {immutable_dmg}")

    # A previous release helper may have left the immutable DMG path as a
    # symlink to the source DMG. shutil.copy2() follows that symlink and then
    # raises SameFileError because source and destination resolve to the same
    # inode. Remove any existing file/symlink first, then copy a real file.
    if immutable_dmg.exists() or immutable_dmg.is_symlink():
        immutable_dmg.unlink()

    shutil.copy2(build.dmg, immutable_dmg)

    if immutable_sha.exists() or immutable_sha.is_symlink():
        immutable_sha.unlink()
    immutable_sha.write_text(f"{actual_sha}  {immutable_dmg.name}\n")

    # Relative links survive clones and GitHub displays them correctly.
    for link in (latest_link, latest_sha_link):
        if link.exists() or link.is_symlink():
            link.unlink()

    latest_link.symlink_to(immutable_dmg.name)
    latest_sha_link.symlink_to(immutable_sha.name)

    notes.write_text(
        f"# AVRET {build.version} — macOS Universal\n\n"
        f"**Build:** {build.build}  \n"
        f"**Platform:** macOS  \n"
        f"**Architecture:** Universal — Apple silicon and Intel  \n\n"
        "This is the current public production release of AVRET®.\n\n"
        "The production DMG is Apple Developer ID signed and notarized.\n\n"
        "## Download\n\n"
        f"- `{immutable_dmg.name}`\n"
        f"- `{immutable_sha.name}`\n"
        "- `AVRET-latest.dmg` points to the current immutable release.\n"
        "- `AVRET-latest.sha256` points to the current checksum.\n\n"
        "## SHA-256\n\n"
        f"```text\n{actual_sha}\n```\n\n"
        "## Author / Lead Design Engineer\n\n"
        "**Brian Ignomirello (IEEE)**\n\n"
        "## Source Code\n\n"
        "AVRET source code is proprietary and is not included in this repository.\n"
    )

    if blob_strategy == "lfs":
        run(["git", "lfs", "install", "--local"], cwd=root)
        run(["git", "lfs", "track", "release/*.dmg"], cwd=root)
        print("Git LFS tracking enabled for release/*.dmg")

    return immutable_dmg, immutable_sha, latest_link, latest_sha_link, notes


def update_readme(build: Build, actual_sha: str):
    readme = repo_root() / "README.md"
    if not readme.exists():
        return

    text = readme.read_text()
    # Update simple known version/build/checksum values if present.
    text = re.sub(r"\*\*Version:\*\*\s*[0-9.]+", f"**Version:** {build.version}", text)
    text = re.sub(r"\*\*Build:\*\*\s*\d+", f"**Build:** {build.build}", text)
    text = re.sub(r"\b[0-9a-f]{64}\b", actual_sha, text, flags=re.I)

    author = (
        "## Author / Lead Design Engineer\n\n"
        "**Brian Ignomirello (IEEE)**\n\n"
        "Morpheus Innovation Labs LLC\n\n"
    )
    if "## Author / Lead Design Engineer" not in text:
        marker = "## Publisher"
        if marker in text:
            text = text.replace(marker, author + marker)
        else:
            text += "\n\n" + author

    readme.write_text(text)


def commit_and_push(build: Build):
    root = repo_root()
    print("\n=== GIT COMMIT / PUSH ===")

    # Stage public distribution material only.
    paths = [
        ".gitignore",
        "README.md",
        "NOTICE.md",
        "SECURITY.md",
        "assets",
        "release",
        "scripts/avret_git_release.py",
    ]
    if (root / ".gitattributes").exists():
        paths.append(".gitattributes")

    run(["git", "add", "--"] + paths, cwd=root)

    status = run(["git", "status", "--short"], cwd=root, capture=True).stdout
    print(status or "No Git changes to commit.")

    cached = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root)
    if cached.returncode != 0:
        run(["git", "commit", "-m", f"AVRET {build.version} build {build.build} public release"], cwd=root)

    run(["git", "branch", "-M", "main"], cwd=root)
    run(["git", "push", "-u", "origin", "main"], cwd=root)


def github_release(build: Build, immutable_dmg: Path, immutable_sha: Path, notes: Path):
    gh = shutil.which("gh")
    if not gh:
        raise SystemExit(
            "\nGit push completed, but GitHub CLI (gh) is not installed.\n"
            "Install with: brew install gh\n"
            "Then authenticate the Morpheus account and rerun."
        )

    print("\n=== GITHUB RELEASE ===")
    exists = subprocess.run(
        [gh, "release", "view", build.tag, "--repo", GITHUB_REPO],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0

    if exists:
        run([
            gh, "release", "upload", build.tag,
            str(immutable_dmg), str(immutable_sha),
            "--clobber", "--repo", GITHUB_REPO
        ])
        run([
            gh, "release", "edit", build.tag,
            "--title", build.title,
            "--notes-file", str(notes),
            "--repo", GITHUB_REPO
        ])
    else:
        run([
            gh, "release", "create", build.tag,
            str(immutable_dmg), str(immutable_sha),
            "--title", build.title,
            "--notes-file", str(notes),
            "--latest",
            "--repo", GITHUB_REPO
        ])


def show_plan(build: Build):
    print("\n" + "=" * 72)
    print("AVRET PUBLIC GITHUB RELEASE MANAGER")
    print("=" * 72)
    print(f"Repository:  {repo_root()}")
    print(f"Dist root:   {dist_root()}")
    print(f"GitHub:      https://github.com/{GITHUB_REPO}")
    print(f"SSH remote:  {SSH_REMOTE}")
    print(f"Selected:    AVRET {build.version} build {build.build}")
    print(f"DMG:         {build.dmg}")
    print("=" * 72)


def main():
    build = choose_build()
    show_plan(build)

    print("\nActions:")
    print("  1. Verify only")
    print("  2. Stage release files only")
    print("  3. Stage + Git commit/push")
    print("  4. FULL release: verify + stage + push + GitHub Release")
    print("  5. Quit")
    choice = input("\nSelect [4]: ").strip() or "4"

    if choice == "5":
        return

    actual = verify(build)

    if choice == "1":
        return

    ensure_git_repo()
    strategy = github_blob_strategy(build)
    staged = stage_release(build, actual, strategy)
    update_readme(build, actual)

    if choice == "2":
        print("\nStaging complete. Nothing was pushed.")
        return

    commit_and_push(build)

    if choice == "3":
        print("\nGit push complete. GitHub Release assets were not changed.")
        return

    if choice == "4":
        immutable_dmg, immutable_sha, _, _, notes = staged
        github_release(build, immutable_dmg, immutable_sha, notes)
        print("\nDONE.")
        print(f"Repository: https://github.com/{GITHUB_REPO}")
        print(f"Tag:        {build.tag}")
        print(f"Latest:     release/AVRET-latest.dmg -> {immutable_dmg.name}")
        return

    raise SystemExit("Invalid menu selection.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
