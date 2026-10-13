//! Interface language. English is the source: a string in code is its own English key, and the
//! Arabic catalog (`ar.tsv`, one `English<TAB>Arabic` row per string) maps it at draw time. A key
//! without a row is shown in English. Engine, control channel, MCP and CLI never see translated
//! text.
//!
//! - [`tl!`] (`tl!("Open")`): a string literal in the current language.
//! - [`tr`]: a string built at run time (menu labels, command labels) in the current language.
//!
//! Arabic is right to left: [`Language::is_rtl`] drives `egui::set_rtl` (vendor/egui, studio/RTL.md)
//! in `lib.rs`, and the catalog stores Arabic in visual order (see [`bidi`]).

pub mod bidi;

use std::collections::HashMap;
use std::sync::OnceLock;
use std::sync::atomic::{AtomicBool, Ordering};

const AR_TSV: &str = include_str!("ar.tsv");

/// Whether the Arabic catalog is in use. English by default.
static ARABIC: AtomicBool = AtomicBool::new(false);

/// The interface language (`ui.language {"lang": …}`, saved in the UI prefs).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Language {
    #[default]
    English,
    Arabic,
}

impl Language {
    pub const ALL: [Self; 2] = [Self::English, Self::Arabic];

    /// The language's name in itself, as the Appearance dropdown shows it.
    pub const fn label(self) -> &'static str {
        match self {
            Self::English => "English",
            Self::Arabic => "العربية",
        }
    }

    /// The id used in `ui.language {"lang": …}`.
    pub const fn id(self) -> &'static str {
        match self {
            Self::English => "en",
            Self::Arabic => "ar",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        Self::ALL.into_iter().find(|l| l.id().eq_ignore_ascii_case(s.trim()))
    }

    pub const fn is_rtl(self) -> bool {
        matches!(self, Self::Arabic)
    }
}

/// Makes `lang` the language of every string drawn from now on. Call once per frame.
pub fn set_language(lang: Language) {
    ARABIC.store(lang == Language::Arabic, Ordering::Relaxed);
}

pub fn is_arabic() -> bool {
    ARABIC.load(Ordering::Relaxed)
}

/// English → Arabic (visual order), parsed once.
fn table() -> &'static HashMap<&'static str, &'static str> {
    static TABLE: OnceLock<HashMap<&'static str, &'static str>> = OnceLock::new();
    TABLE.get_or_init(|| {
        AR_TSV
            .lines()
            .filter(|l| !l.is_empty() && !l.starts_with('#'))
            .filter_map(|l| l.split_once('\t'))
            .map(|(en, ar)| {
                let visual: &'static str = Box::leak(bidi::visual(ar).into_boxed_str());
                (en, visual)
            })
            .collect()
    })
}

/// `s` in the Arabic catalog when `arabic`, else `s` itself.
fn pick(arabic: bool, s: &str) -> &str {
    if !arabic {
        return s;
    }
    table().get(s).copied().unwrap_or(s)
}

/// `s` in the current language. Use through [`tl!`].
pub fn t(s: &'static str) -> &'static str {
    pick(is_arabic(), s)
}

/// `s` in the current language, for text built at run time.
pub fn tr(s: &str) -> &str {
    pick(is_arabic(), s)
}

/// A string literal in the current language. The literal is the key, so it stays readable in code.
#[macro_export]
macro_rules! tl {
    ($s:literal) => {
        $crate::i18n::t($s)
    };
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The `tl!("…")` literals of the crate's sources, in file order.
    fn tl_literals(dir: &std::path::Path, out: &mut Vec<String>) {
        for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
            let path = entry.path();
            if path.is_dir() {
                tl_literals(&path, out);
            } else if path.extension().is_some_and(|e| e == "rs") {
                let text = std::fs::read_to_string(&path).unwrap_or_default();
                let mut rest = text.as_str();
                while let Some(at) = rest.find("tl!(\"") {
                    rest = &rest[at + 5..];
                    if let Some(end) = rest.find('"') {
                        out.push(rest[..end].to_string());
                    }
                }
            }
        }
    }

    #[test]
    fn every_tl_literal_has_an_arabic_row() {
        let mut literals = Vec::new();
        tl_literals(std::path::Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/src")), &mut literals);
        assert!(literals.len() > 100, "found only {} tl! literals", literals.len());
        let missing: Vec<&String> = literals.iter().filter(|s| !table().contains_key(s.as_str())).collect();
        assert!(missing.is_empty(), "tl! literals without an ar.tsv row: {missing:?}");
    }

    #[test]
    fn every_menu_label_has_an_arabic_row() {
        fn walk(nodes: &[crate::menus::MenuNode], missing: &mut Vec<String>) {
            for n in nodes {
                if !table().contains_key(n.label.as_str()) {
                    missing.push(n.label.clone());
                }
                walk(&n.children, missing);
            }
        }
        let mut missing = Vec::new();
        walk(&crate::menus::tree(), &mut missing);
        for (_, label, _, _) in crate::menus::UI_COMMANDS {
            if !table().contains_key(label) {
                missing.push((*label).to_string());
            }
        }
        missing.sort();
        missing.dedup();
        assert!(missing.is_empty(), "menu labels without an ar.tsv row: {missing:?}");
    }

    #[test]
    fn rows_are_unique_and_well_formed() {
        let mut seen = std::collections::HashSet::new();
        for line in AR_TSV.lines().filter(|l| !l.is_empty() && !l.starts_with('#')) {
            let (en, ar) = line.split_once('\t').unwrap_or_else(|| panic!("no tab in row: {line}"));
            assert!(!en.is_empty() && !ar.is_empty(), "empty cell in row: {line}");
            assert!(seen.insert(en), "duplicate row: {en}");
        }
    }

    #[test]
    fn arabic_lookup_maps_known_keys_only() {
        // `pick` takes the language explicitly, so no test flips the process-wide switch.
        assert_eq!(pick(true, "Open"), table()["Open"]);
        assert_eq!(pick(true, "not in the catalog"), "not in the catalog");
        assert_eq!(pick(false, "Open"), "Open");
    }

    #[test]
    fn language_ids_round_trip() {
        for lang in Language::ALL {
            assert_eq!(Language::parse(lang.id()), Some(lang));
        }
        assert_eq!(Language::parse(" AR "), Some(Language::Arabic));
        assert_eq!(Language::parse("fr"), None);
        assert!(Language::Arabic.is_rtl() && !Language::English.is_rtl());
    }
}
