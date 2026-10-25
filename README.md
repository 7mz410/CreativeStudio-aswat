<p align="center">
  <img alt="aswat" src="docs/studio/aswat.svg" width="140">
</p>

<h1 align="center">aswat</h1>

<p align="center">
  <b>Free, open-source audio editing — part of the Creative Studio creative suite.</b><br>
  <b>تحرير الصوت، مجاني ومفتوح المصدر — جزء من حزمة Creative Studio.</b>
</p>

<p align="center">
  <a href="https://aswat.studio.creative.ps/">aswat.studio.creative.ps</a> ·
  <a href="https://studio.creative.ps/">studio.creative.ps</a>
</p>

<p align="center">
  <img alt="License: MIT OR Apache-2.0" src="https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-555555">
  <img alt="Based on SoundCraft" src="https://img.shields.io/badge/based%20on-SoundCraft-0d2d3f">
</p>

## Built on SoundCraft

aswat is a fork of **[SoundCraft](https://github.com/storytold/soundcraft)**, the open-source, clean-room
application written in Rust by the **[ArtCraft](https://getartcraft.com/)** team and the SoundCraft
contributors. Almost everything that makes this app work is their work. Thank you. If you like
aswat, please star and support the upstream project as well.

What we add: the Creative Studio identity, the Arabic interface laid out right to left, and Arabic
features to come. Our changes are listed in [`studio/CHANGES.md`](studio/CHANGES.md).
Upstream's own README, with the full feature list and build instructions, is in
[`docs/UPSTREAM-README.md`](docs/UPSTREAM-README.md).

## The Creative Studio suite

Fifteen free, open-source apps with an Arabic interface laid out right to left. [mansa (المنصّة)](https://github.com/7mz410/CreativeStudio-mansa) installs and updates them all. The whole suite: [github.com/7mz410/CreativeStudio](https://github.com/7mz410/CreativeStudio) · [studio.creative.ps](https://studio.creative.ps/).

| App | | What it's for | Saves as | Based on |
|---|---|---|---|---|
| [rsm](https://github.com/7mz410/CreativeStudio-rsm) | رسم | Vector illustration | `.rsm` | VectorCraft |
| [7rrek](https://github.com/7mz410/CreativeStudio-7rrek) | حرّك | Animation | `.7rrek` | VectorCraft (via rsm) |
| [tlween](https://github.com/7mz410/CreativeStudio-tlween) | تلوين | Image editing | `.tlween` | PhotoCraft |
| [lamasat](https://github.com/7mz410/CreativeStudio-lamasat) | لمسات | Photo library and raw development | — | LightCraft |
| [tsweer](https://github.com/7mz410/CreativeStudio-tsweer) | تصوير | Video editing | `.tsweer` | FilmCraft |
| [effectat](https://github.com/7mz410/CreativeStudio-effectat) | تأثيرات | Motion graphics and effects | `.effectat` | EffectCraft |
| **aswat** | أصوات | Audio recording and mixing | `.aswat` | SoundCraft |
| [al7an](https://github.com/7mz410/CreativeStudio-al7an) | ألحان | Music making | `.al7an` | SoundCraft |
| [trteeb](https://github.com/7mz410/CreativeStudio-trteeb) | ترتيب | Page layout | `.trteeb` | DesignCraft |
| [sharek](https://github.com/7mz410/CreativeStudio-sharek) | شارك | Interface and graphic design | `.sharek` | FigCraft |
| [sf7aat](https://github.com/7mz410/CreativeStudio-sf7aat) | صفحات | PDF documents | `.pdf` | PdfCraft |
| [klmat](https://github.com/7mz410/CreativeStudio-klmat) | كلمات | Word processing | `.docx` | WordCraft |
| [arqam](https://github.com/7mz410/CreativeStudio-arqam) | أرقام | Spreadsheets | `.xlsx` | GridCraft |
| [3urood](https://github.com/7mz410/CreativeStudio-3urood) | عروض | Presentations | `.3urood` | DeckCraft |
| [muhandes](https://github.com/7mz410/CreativeStudio-muhandes) | مهندس | Computer-aided design | `.dxf` | CADCraft |

## Building

```sh
cargo run --release -p soundcraft
# after merging upstream:
git fetch upstream && git merge upstream/main && python3 studio/rebrand.py
```

## Licence

Code: MIT OR Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE`), like upstream. The Creative Studio
name and logos in `docs/studio/` belong to the Creative Studio project.
