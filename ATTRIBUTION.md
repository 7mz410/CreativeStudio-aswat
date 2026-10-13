# Attribution

Every asset bundled with or committed to SoundCraft is listed here with its author, source and
license. `cargo xtask assets` fails CI when a tracked asset file has no row.

**Rule:** no Avid, Pro Tools, Adobe or other proprietary icons, images, sounds or presets — ever.
Assets must be original, public domain (CC0) or permissively licensed. See `AGENTS.md`.

## Icons

All UI icons (tools, transport, track buttons) are drawn procedurally in
`crates/ui-egui/src/icons.rs` by the SoundCraft contributors (MIT OR Apache-2.0). No UI icon image
files are used. The app icon (`assets/app-icon/`, the aswat star by Hamza Abu Ayyash for Creative Studio) is listed under Files below.

## Audio

The demo session's audio (drums, bass, pad) and its MIDI parts are synthesised in code in
`crates/engine/src/demo.rs` by the SoundCraft contributors (MIT OR Apache-2.0). No sample files
are bundled.

## Fonts

SoundCraft bundles no font files. It uses the default fonts shipped inside the `egui` crate
(Ubuntu-Light: Ubuntu Font Licence 1.0; Hack: MIT; Noto Emoji: OFL-1.1; emoji-icon-font: OFL-1.1/MIT)
and, at runtime, the operating system's own UI fonts when available (never redistributed).

## Files

| Path | Author | Source | License |
|---|---|---|---|
| `docs/studio/aswat.svg` | Hamza Abu Ayyash (Creative Studio) | Original artwork | MIT OR Apache-2.0 |
| `assets/app-icon/icon.svg` | Hamza Abu Ayyash (Creative Studio) | the aswat star (`docs/studio/aswat.svg`) on a white tile, rendered by `packaging/icons.sh` | MIT OR Apache-2.0 |
| `packaging/macos/dmg/` (all files) | @XusBadia | original (macOS DMG window background and layout, from the app icon; see `packaging/macos/dmg/README.md`) | MIT OR Apache-2.0 |
| `assets/app-icon/soundcraft-1024.png` | Hamza Abu Ayyash (Creative Studio) | the aswat star (`docs/studio/aswat.svg`) on a white tile, rendered by `packaging/icons.sh` | MIT OR Apache-2.0 |
| `assets/app-icon/soundcraft-macos-512.png` | Hamza Abu Ayyash (Creative Studio) | the aswat star (`docs/studio/aswat.svg`) on a white tile, rendered by `packaging/icons.sh` | MIT OR Apache-2.0 |
| `assets/app-icon/soundcraft.icns` | Hamza Abu Ayyash (Creative Studio) | the aswat star (`docs/studio/aswat.svg`) on a white tile, rendered by `packaging/icons.sh` | MIT OR Apache-2.0 |
| `assets/app-icon/soundcraft.ico` | Hamza Abu Ayyash (Creative Studio) | the aswat star (`docs/studio/aswat.svg`) on a white tile, rendered by `packaging/icons.sh` | MIT OR Apache-2.0 |
| `assets/app-icon/hicolor/` | Hamza Abu Ayyash (Creative Studio) | the aswat star (`docs/studio/aswat.svg`) on a white tile, rendered by `packaging/icons.sh` | MIT OR Apache-2.0 |
| `docs/images/` | SoundCraft contributors | screenshots of SoundCraft rendered from the synthesised demo session | MIT OR Apache-2.0 |
