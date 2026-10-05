# AVRET®

<p align="center">
  <img src="assets/welcomeAvret.png" alt="AVRET Platform" width="900">
</p>

**AVRET® — Advanced Research, Editing and Testing** is a native macOS engineering workbench for Microchip AVR devices.

> **This repository is for public binary distribution only. AVRET application source code is proprietary and is not published here.**

## Current Release

**Version:** 1.1.6  
**Build:** 26081203  
**Platform:** macOS 13.5+  
**Architecture:** Universal — Apple silicon and Intel  
**Status:** Apple Developer ID signed and notarized

### Release assets

```text
AVRET-1.1.6-b26081203.dmg
AVRET-1.1.6-b26081203.dmg.sha256
```

SHA-256:

```text
711660764310b8c3bc530fbe7ac556005ca5d14cd11e48ee56fa58745bbb95fc
```

## Install

1. Open the latest GitHub Release.
2. Download `AVRET-1.1.6-b26081203.dmg`.
3. Optionally verify the checksum.
4. Open the DMG.
5. Drag AVRET to Applications.
6. Launch AVRET.

## Verify

```bash
shasum -a 256 "AVRET-1.1.6-b26081203.dmg"
```

Expected:

```text
711660764310b8c3bc530fbe7ac556005ca5d14cd11e48ee56fa58745bbb95fc
```

Or:

```bash
shasum -a 256 -c "AVRET-1.1.6-b26081203.dmg.sha256"
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

## Source Code

No AVRET application source code is published in this repository.

## Microchip Notice

AVRET is an independent commercial utility. It is not affiliated with, endorsed by, or sponsored by Microchip Technology Inc.

Microchip, AVR, Atmel, and related marks are the property of their respective owners.

## Author / Lead Design Engineer

**Brian Ignomirello (IEEE)**

Morpheus Innovation Labs LLC

## Publisher

**Morpheus Innovation Labs LLC**

Copyright © 2026 Morpheus Innovation Labs LLC. All rights reserved.
