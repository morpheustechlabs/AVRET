# AVRET®

AVRET® — Advanced Research, Editing and Testing is a native macOS engineering workbench for Microchip AVR devices.

> This repository is for public AVRET binary distribution.

## Current Release

Version: 1.1.7
Build: 2610051921
Platform: macOS 13.5+
Architecture: Universal — Apple silicon and Intel
Status: Apple Developer ID signed and notarized
Direct download: https://avret.morpheusinnovation.com/downloads/AVRET-1.1.7-b2610051921.dmg?avret_release=8997df82f7880c82

### Release assets

- `AVRET-1.1.7-b2610051921.dmg` — GitHub Release asset / AVRET download service
- `AVRET-latest.sha256` — checksum for the current installer
- `RELEASE-NOTES-v1.1.7.md` — current release notes

SHA-256:

```text
8997df82f7880c825b69e67aaa0ef7920a67e08411d62e079a9a551dfe4fb487
```

## Install

1. Open the latest GitHub Release.
2. Download `AVRET-1.1.7-b2610051921.dmg`.
3. Optionally verify the checksum.
4. Open the DMG.
5. Drag AVRET to Applications.
6. Launch AVRET.

## Verify

```sh
shasum -a 256 "AVRET-1.1.7-b2610051921.dmg"
```

Expected:

```text
8997df82f7880c825b69e67aaa0ef7920a67e08411d62e079a9a551dfe4fb487
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
