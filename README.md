# AVRET®

AVRET® — Advanced Research, Editing and Testing is a native macOS engineering workbench for Microchip AVR devices.

> This repository is for public AVRET binary distribution.

## Current Release

Version: 1.1.8
Build: 2610061221
Platform: macOS 13.5+
Architecture: Universal — Apple silicon and Intel
Status: Apple Developer ID signed and notarized
Direct download: https://avret.morpheusinnovation.com/downloads/AVRET-1.1.8-b2610061221.dmg?avret_release=5eaccd63d49636bf

### Release assets

- `AVRET-1.1.8-b2610061221.dmg` — GitHub Release asset / AVRET download service
- `AVRET-latest.sha256` — checksum for the current installer
- `RELEASE-NOTES-v1.1.8.md` — current release notes

SHA-256:

```text
5eaccd63d49636bf30995ef0a656e75aa570434e86dac81a41e2192cfad1cd1c
```

## Install

1. Open the latest GitHub Release.
2. Download `AVRET-1.1.8-b2610061221.dmg`.
3. Optionally verify the checksum.
4. Open the DMG.
5. Drag AVRET to Applications.
6. Launch AVRET.

## Verify

```sh
shasum -a 256 "AVRET-1.1.8-b2610061221.dmg"
```

Expected:

```text
5eaccd63d49636bf30995ef0a656e75aa570434e86dac81a41e2192cfad1cd1c
```

## What AVRET Provides

- AVR programmer discovery and hardware identification
- Target signature probing and verification
- Flash, EEPROM, User Signature, HEX, BIN, EEP, and ELF workflows
- Visual compare and backup workflows
- Device-image and cloning workflows
- Fuse and EEPROM tools
- AVR disassembly and analysis
- Package-aware pin visualization
- Device Pack integration
- Engineering calculators and bitwise utilities

## Microchip Notice

AVRET is an independent commercial utility. It is not affiliated with, endorsed by, or sponsored by Microchip Technology Inc.

Microchip, AVR, Atmel, and related marks are the property of their respective owners.

## Author / Lead Design Engineer

Brian Ignomirello (IEEE)

Morpheus Innovation Labs LLC

## Publisher

Morpheus Innovation Labs LLC

Copyright © 2026 Morpheus Innovation Labs LLC. All rights reserved.
