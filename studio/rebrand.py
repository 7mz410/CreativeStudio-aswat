#!/usr/bin/env python3
"""Apply the aswat (Creative Studio) branding on top of upstream SoundCraft.

Only user-visible text is rebranded; crate names, the file format and other internals keep their
upstream names so `git merge upstream/main` stays easy. The script is idempotent: after merging
upstream, resolve any conflicts in favour of upstream and run it again.

    python3 studio/rebrand.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = 'aswat'
REPO = 'https://github.com/7mz410/CreativeStudio-aswat'
SITE = 'https://studio.creative.ps'
APP_SITE = 'https://aswat.studio.creative.ps'
# Persisted names and legal lines; renaming them would lose settings or misstate copyright.
KEEP = ('by the ArtCraft team', 'Application Support/SoundCraft', '/roaming/SoundCraft', 'the SoundCraft authors', 'SoundCraft contributors', 'SOUNDCRAFT_')
# Persisted names whose literal is just "SoundCraft": eframe's storage name and the Windows settings folder.
PROTECT = ('eframe::run_native(\n        "SoundCraft"', '.join("SoundCraft")')

# (file, upstream text, our text[, marker meaning "already applied"]). The upstream text may also
# be found in its renamed form (after the general rename below).
RULES = [
    # About: our links and credit line, no Discord.
    ('crates/ui-egui/src/panels.rs', 'ui.label("An open-source digital audio workstation from the ArtCraft team.");',
     'ui.label("An open-source digital audio workstation, part of the Creative Studio suite.\\nBuilt on SoundCraft by the ArtCraft team.");'),
    ('crates/ui-egui/src/panels.rs', 'ui.hyperlink_to("getartcraft.com/apps/soundcraft", "https://getartcraft.com/apps/soundcraft");',
     f'ui.hyperlink_to("aswat.studio.creative.ps", "{APP_SITE}");'),
    ('crates/ui-egui/src/panels.rs', 'ui.hyperlink_to("Join us on Discord", "https://discord.gg/artcraft");',
     f'ui.hyperlink_to("Source code: github.com/7mz410/CreativeStudio-aswat", "{REPO}");'),
    ('crates/clap-host/src/ffi.rs', 'url: c"https://github.com/storytold/soundcraft".as_ptr(),', f'url: c"{REPO}".as_ptr(),'),
    # Web page and packages.
    ('apps/soundcraft-web/index.html', '<title>SoundCraft</title>', f'<title>{NAME}</title>'),
    ('apps/soundcraft-web/index.html', 'Loading SoundCraft&hellip;', f'Loading {NAME}&hellip;'),
    ('packaging/macos/Info.plist.in', '<string>ai.storyteller.soundcraft</string>', '<string>ps.creative.studio.aswat</string>'),
    ('packaging/windows/soundcraft.wxs', '<Property Id="ARPURLINFOABOUT" Value="https://getartcraft.com/apps/soundcraft" />', f'<Property Id="ARPURLINFOABOUT" Value="{APP_SITE}" />'),
    ('packaging/windows/soundcraft.wxs', '<Property Id="ARPURLUPDATEINFO" Value="https://getartcraft.com/apps/soundcraft" />', f'<Property Id="ARPURLUPDATEINFO" Value="{REPO}/releases" />'),
    ('packaging/windows/soundcraft.wxs', '<Property Id="ARPHELPLINK" Value="https://discord.gg/artcraft" />', f'<Property Id="ARPHELPLINK" Value="{REPO}/issues" />'),
    ('packaging/windows/sign.ps1', "'/du', 'https://github.com/storytold/soundcraft'", f"'/du', '{REPO}'"),
    ('packaging/linux/nfpm.yaml', 'homepage: https://getartcraft.com/apps/soundcraft', f'homepage: {APP_SITE}'),
    ('packaging/linux/ai.storyteller.soundcraft.desktop', 'Name=SoundCraft\n', f'Name={NAME}\n'),
    ('packaging/linux/ai.storyteller.soundcraft.metainfo.xml.in', '  <name>SoundCraft</name>', f'  <name>{NAME}</name>'),
    ('packaging/linux/ai.storyteller.soundcraft.metainfo.xml.in', '<url type="homepage">https://getartcraft.com/apps/soundcraft</url>', f'<url type="homepage">{APP_SITE}</url>'),
    ('packaging/linux/ai.storyteller.soundcraft.metainfo.xml.in', '<url type="bugtracker">https://github.com/storytold/soundcraft/issues</url>', f'<url type="bugtracker">{REPO}/issues</url>'),
    ('packaging/linux/ai.storyteller.soundcraft.metainfo.xml.in', '<url type="help">https://github.com/storytold/soundcraft</url>', f'<url type="help">{REPO}</url>'),
    ('packaging/linux/ai.storyteller.soundcraft.metainfo.xml.in', '<url type="contact">https://discord.gg/artcraft</url>', f'<url type="contact">{SITE}</url>'),
]
# Text in string literals and catalogs, before the general rename.
LITERALS = []
STRING = re.compile(r'"(?:[^"\\\n]|\\.)*"')


def rename(lit: str) -> str:
    for a, b in LITERALS:
        lit = lit.replace(a, b)
    if any(k in lit for k in KEEP):
        return lit
    return lit.replace('SoundCraft', NAME)


def renamed_code(text: str) -> str:
    held = {f'\0{i}\0': k for i, k in enumerate(PROTECT)}
    for h, k in held.items():
        text = text.replace(k, h)
    text = STRING.sub(lambda m: rename(m.group(0)), text)
    for h, k in held.items():
        text = text.replace(h, k)
    return text


def apply_rules() -> list:
    changed = []
    for rel, a, b, *marker in RULES:
        p = ROOT / rel
        s = p.read_text(encoding='utf-8')
        if marker and marker[0] in s:
            continue
        if a not in s and renamed_code(a) in s:
            a = renamed_code(a)  # the general rename got there first
        if a not in s or (b and a in b and b in s):
            if not b or b in s or renamed_code(b) in s:
                continue  # already applied
            print(f'warning: {rel}: upstream text not found (did upstream change it?): {a[:70]!r}')
            continue
        p.write_text(s.replace(a, b), encoding='utf-8')
        changed.append(rel)
    return changed


def rename_sources() -> list:
    changed = []
    for p in sorted((ROOT / 'crates/ui-egui').rglob('*.rs')) + [q for q in sorted((ROOT / 'crates/engine').rglob('*.rs')) if not q.name.startswith('tests') and 'tests' not in q.parts] + sorted((ROOT / 'apps').rglob('*.rs')):
        s = p.read_text(encoding='utf-8')
        o = renamed_code(s)
        if o != s:
            p.write_text(o, encoding='utf-8')
            changed.append(p.relative_to(ROOT).as_posix())
    plist = ROOT / 'packaging/macos/Info.plist.in'
    s = plist.read_text(encoding='utf-8')
    o = re.sub(r'(<key>CFBundle(?:Display|Executable)?Name</key>\s*<string>)SoundCraft(</string>)', rf'\g<1>{NAME}\2', s)
    if o != s:
        plist.write_text(o, encoding='utf-8')
        changed.append('packaging/macos/Info.plist.in')
    return changed


def main():
    changed = apply_rules() + rename_sources()
    for c in sorted(set(changed)):
        print('rebranded', c)


# Creative Studio: the macOS app folder in the .dmg and the volume name carry our name
# (packaging/macos/package.sh). Bundle and binary names inside the package stay as upstream has them.
PACKAGING_NAMES = {
    'packaging/macos/package.sh': [
        ('SoundCraft.app', 'aswat.app'),
        ('-volname "SoundCraft"', '-volname "aswat"'),
        ('-hfs-volume-name "SoundCraft"', '-hfs-volume-name "aswat"'),
    ],
}


def apply_packaging_names() -> list:
    changed = []
    for rel, pairs in PACKAGING_NAMES.items():
        path = ROOT / rel
        src = path.read_text(encoding='utf-8')
        out = src
        for a, b in pairs:
            out = out.replace(a, b)
        if out != src:
            path.write_text(out, encoding='utf-8')
            changed.append(path)
    return changed


if __name__ == '__main__':
    main()
    for _p in apply_packaging_names():
        print('rebranded', _p.relative_to(ROOT))
