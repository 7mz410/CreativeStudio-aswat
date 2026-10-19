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
KEEP = ('by the ArtCraft team', 'Application Support/SoundCraft', '/roaming/SoundCraft', 'the SoundCraft authors', 'SoundCraft contributors', 'SOUNDCRAFT_', 'SoundCraftData')
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
# Creative Studio: sessions save as `.aswat` (own extension, own document icon); upstream's `.scraft`
# still opens. Same approach as rsm (STUDIO_EXTENSION next to upstream's). Applied by apply_rules.
RULES += [
    ('crates/model/src/session.rs', r'''pub const SESSION_EXTENSION: &str = "scraft";''',
     r'''pub const SESSION_EXTENSION: &str = "scraft";
/// Creative Studio saves sessions as `.aswat`; upstream's `.scraft` still opens.
pub const STUDIO_EXTENSION: &str = "aswat";'''),
    ('crates/model/src/lib.rs', 'MAX_NAME_CHARS, SESSION_EXTENSION, Session,',
     'MAX_NAME_CHARS, SESSION_EXTENSION, STUDIO_EXTENSION, Session,'),
    ('crates/engine/src/io.rs', 'with `.scraft` added when it has no',
     'with `.aswat` added when it has no'),
    ('crates/engine/src/io.rs', 'p.with_extension(soundcraft_model::SESSION_EXTENSION) } else { p }',
     'p.with_extension(soundcraft_model::STUDIO_EXTENSION) } else { p }'),
    ('crates/engine/src/cmd/file.rs', 'p.extension().is_some_and(|x| x != "scraft")',
     'p.extension().is_some_and(|x| x != "scraft" && x != "aswat")'),
    ('crates/engine/src/cmd/file.rs', '    #[test]\n    fn save_copy_leaves_the_open_session_alone() {',
     r'''    #[test]
    fn sessions_save_as_aswat_and_scraft_still_opens() {
        let (mut e, _) = tone_engine();
        let dir = std::env::temp_dir().join(format!("sc-aswat-ext-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        e.execute("session.save_as", &json!({"path": dir.join("Plain").to_string_lossy()})).unwrap();
        assert!(dir.join("Plain.aswat").is_file(), "a name without an extension saves as .aswat");
        let old = dir.join("Old.scraft");
        std::fs::copy(dir.join("Plain.aswat"), &old).unwrap();
        let mut opened = Engine::default();
        opened.execute("session.open", &json!({"path": old.to_string_lossy()})).unwrap();
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn save_copy_leaves_the_open_session_alone() {'''),
    ('apps/soundcraft/src/main.rs', '//! Usage: `soundcraft [--demo] [--control <port>] [--no-audio] [session.scraft | audio files…]`',
     '//! Usage: `soundcraft [--demo] [--control <port>] [--no-audio] [session.aswat | session.scraft | audio files…]`'),
    ('apps/soundcraft/src/main.rs', 'let r = if lower.ends_with(".scraft") {',
     'let r = if lower.ends_with(".scraft") || lower.ends_with(".aswat") {'),
    ('apps/soundcraft/src/main.rs', '"session.open" => d.add_filter("aswat Session", &["scraft"]),',
     '"session.open" => d.add_filter("aswat Session", &["aswat", "scraft"]),'),
    ('apps/soundcraft/src/main.rs', '_ => rfd::FileDialog::new().add_filter("aswat Session", &["scraft"]),',
     '_ => rfd::FileDialog::new().add_filter("aswat Session", &["aswat", "scraft"]),'),
    ('apps/soundcraft-cli/src/main.rs', 'if path.ends_with(".scraft") {',
     'if path.ends_with(".scraft") || path.ends_with(".aswat") {'),
    ('crates/ui-egui/src/windows.rs', '"midi", "scraft"].contains(&ext.as_str()))',
     '"midi", "scraft", "aswat"].contains(&ext.as_str()))'),
    ('apps/soundcraft-web/src/web.rs', 'const SESSION_EXTS: &[&str] = &[io::BUNDLE_EXTENSION, soundcraft_model::SESSION_EXTENSION];',
     'const SESSION_EXTS: &[&str] = &[io::BUNDLE_EXTENSION, soundcraft_model::STUDIO_EXTENSION, soundcraft_model::SESSION_EXTENSION];'),
    ('apps/soundcraft-web/src/web.rs', 'Some("json" | "scraft") => "application/json",',
     'Some("json" | "scraft" | "aswat") => "application/json",'),
    ('packaging/linux/ai.storyteller.soundcraft.desktop', 'MimeType=application/x-soundcraft-session;',
     'MimeType=application/x-aswat-session;application/x-soundcraft-session;'),
    ('packaging/linux/ai.storyteller.soundcraft.mime.xml', '</mime-info>',
     r'''  <mime-type type="application/x-aswat-session">
    <comment>aswat session</comment>
    <sub-class-of type="application/json"/>
    <icon name="ai.storyteller.soundcraft"/>
    <glob pattern="*.aswat"/>
  </mime-type>
</mime-info>'''),
    ('packaging/windows/soundcraft.wxs', '''          </Extension>
        </ProgId>
        <!-- Audio and MIDI files''',
     '''          </Extension>
          <Extension Id="aswat" ContentType="application/x-aswat-session">
            <Verb Id="open" Command="Open" TargetFile="SoundcraftExe" Argument="&quot;%1&quot;" />
          </Extension>
        </ProgId>
        <!-- Audio and MIDI files'''),
    ('packaging/windows/soundcraft.wxs', r'''Name=".scraft" Value="" Type="string" />''',
     r'''Name=".scraft" Value="" Type="string" />
        <RegistryValue Root="HKLM" Key="Software\Classes\Applications\soundcraft.exe\SupportedTypes" Name=".aswat" Value="" Type="string" />'''),
    ('packaging/macos/Info.plist.in', '''  <key>UTExportedTypeDeclarations</key>
  <array>
''',
     '''  <key>UTExportedTypeDeclarations</key>
  <array>
    <!-- aswat's session: the same JSON file as .scraft, saved with the .aswat extension. -->
    <dict>
      <key>UTTypeIdentifier</key>
      <string>ps.creative.studio.aswat.session</string>
      <key>UTTypeDescription</key>
      <string>aswat Session</string>
      <key>UTTypeConformsTo</key>
      <array>
        <string>public.data</string>
        <string>public.content</string>
      </array>
      <key>UTTypeIconFile</key>
      <string>aswat-document</string>
      <key>UTTypeTagSpecification</key>
      <dict>
        <key>public.filename-extension</key>
        <array><string>aswat</string></array>
        <key>public.mime-type</key>
        <array><string>application/x-aswat-session</string></array>
      </dict>
    </dict>
'''),
    ('packaging/macos/Info.plist.in', '''<key>CFBundleTypeName</key>
      <string>SoundCraft Session</string>''',
     '''<key>CFBundleTypeName</key>
      <string>aswat Session</string>'''),
    ('packaging/macos/Info.plist.in', '''<key>CFBundleTypeIconFile</key>
      <string>SoundCraft</string>
      <key>LSItemContentTypes</key>
      <array><string>ai.storyteller.soundcraft.session</string></array>''',
     '''<key>CFBundleTypeIconFile</key>
      <string>aswat-document</string>
      <key>LSItemContentTypes</key>
      <array><string>ps.creative.studio.aswat.session</string><string>ai.storyteller.soundcraft.session</string></array>'''),
    ('packaging/macos/package.sh', 'cp "$ROOT/assets/app-icon/soundcraft.icns" "$APP/Contents/Resources/SoundCraft.icns"\n',
     'cp "$ROOT/assets/app-icon/soundcraft.icns" "$APP/Contents/Resources/SoundCraft.icns"\ncp "$ROOT/assets/app-icon/aswat-document.icns" "$APP/Contents/Resources/aswat-document.icns"\n'),
    ('ATTRIBUTION.md', '| `assets/app-icon/icon.svg` |',
     '| `assets/app-icon/aswat-document.svg` | Hamza Abu Ayyash (Creative Studio) | original work: the aswat document icon (`file icons/aswat.svg`) | MIT OR Apache-2.0 |\n'
     '| `assets/app-icon/aswat-document.icns` | Hamza Abu Ayyash (Creative Studio) | the aswat document icon (`assets/app-icon/aswat-document.svg`) rendered with rsvg-convert, packed with iconutil; the document icon of `.aswat` sessions | MIT OR Apache-2.0 |\n'
     '| `assets/app-icon/icon.svg` |'),
    ('studio/CHANGES.md', 'settings folders and the file format keep their upstream names.',
     'settings folders and the session JSON keep their upstream names.'),
    ('studio/CHANGES.md', '- No Discord buttons; community links point to Creative Studio.',
     '- No Discord buttons; community links point to Creative Studio.\n'
     '- Sessions save as `.aswat`, with their own document icon (`assets/app-icon/aswat-document.*`). `.scraft`,\n'
     '  upstream\'s extension, still opens.'),
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
