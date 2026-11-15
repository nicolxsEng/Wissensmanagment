"""HTML der Fragetexte in Text umwandeln (plan.md 5.3, K8; docs/datenmodell.md).

Codeblöcke = <pre>-Elemente. Inline-<code> bleibt Teil des Fließtexts.
"""

import html
import re
from dataclasses import dataclass

from selectolax.lexbor import LexborHTMLParser

CODE_PLACEHOLDER = "[CODE]"
_SENTINEL = "\x00"  # markiert die Stelle eines entfernten Codeblocks
_WS = re.compile(r"\s+")


def _collapse(s: str) -> str:
    return _WS.sub(" ", s).strip()


@dataclass(frozen=True, slots=True)
class BodyParts:
    text_nocode: str  # Fließtext ohne Codeblöcke (Grundlage für K8)
    text_for_model: str  # Fließtext mit [CODE] an Stelle der Codeblöcke
    code: str  # Inhalt aller Codeblöcke, durch Leerzeile getrennt
    n_code_blocks: int
    code_chars: int

    @property
    def len_nocode(self) -> int:
        return len(self.text_nocode)


def split_body(body_html: str | None) -> BodyParts:
    """Trennt einen Fragetext in Fließtext und Codeblöcke."""
    tree = LexborHTMLParser(body_html or "")
    blocks = tree.css("pre")
    codes = [b.text(deep=True, separator="") for b in blocks]
    for b in blocks:
        b.replace_with(_SENTINEL)
    root = tree.body
    raw = root.text(deep=True, separator=" ") if root is not None else ""
    text_nocode = _collapse(raw.replace(_SENTINEL, " "))
    text_for_model = _collapse(raw.replace(_SENTINEL, f" {CODE_PLACEHOLDER} "))
    code = "\n\n".join(c.strip("\n") for c in codes)
    return BodyParts(
        text_nocode=text_nocode,
        text_for_model=text_for_model,
        code=code,
        n_code_blocks=len(blocks),
        code_chars=sum(len(c.strip("\n")) for c in codes),
    )


def clean_title(title: str | None) -> str:
    """Titel aus der API enthalten HTML-Entitäten (z. B. &#39;)."""
    return _collapse(html.unescape(title or ""))
