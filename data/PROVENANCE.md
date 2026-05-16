# data/ provenance

## Tractatus Logico-Philosophicus (Wittgenstein — bilingual edition)

Project Gutenberg eBook #5740 is a **bilingual edition** containing both
Wittgenstein's original German text and C. K. Ogden's 1922 English translation
side-by-side, prefaced by Bertrand Russell's introduction.

| Field | Value |
|---|---|
| Title | Tractatus Logico-Philosophicus |
| Author | Ludwig Wittgenstein |
| Original language | German (1921, *Annalen der Naturphilosophie*) |
| Translator (English) | C. K. Ogden |
| Contributor | Bertrand Russell (Introduction) |
| First publication (English) | 1922 (Routledge & Kegan Paul, London) |
| Project Gutenberg eBook | #5740 |
| Release date | 2010-10-22 (revised 2021-12-13) |
| Source URL | <https://www.gutenberg.org/files/5740/5740-t/5740-t.tex> |
| Edition layout | Bilingual: German original + Ogden English translation |
| License | Public Domain in the United States, distributed under the Project Gutenberg License. |

Files:
- `5740-t.tex` — canonical LaTeX source as published by Project Gutenberg (binary-identical to upstream). Contains **both** the German original and the Ogden English translation interleaved; the TeX header declares `Language: German` because the original is German.
- `tractatus.txt` — regex-stripped plain-text approximation derived from the `.tex`. Inherits the bilingual content (German + English are mixed together as a single lossy stream). The conversion is intentionally lossy and is **not** authoritative; cite `5740-t.tex` for any reproduction. See `tractatus_index.json` for SHA-256 of both files.

Notes:
- The German original (Wittgenstein, 1921) and the Ogden translation (1922) are both in the public domain in the United States. Users outside the US should confirm the status under their local copyright law before redistribution.
- The Project Gutenberg header/footer is part of the released eBook and is retained in both files.
- **Why this corpus ships with the package.** `family-resemblance`'s clustering and `[mcp]` modules do not depend on this text at runtime. The Tractatus is included only as a reference for documentation and examples (Phase 5+), to contrast Wittgenstein's *early* picture-theoretic position (*Tractatus*, 1921) with the *later* family-resemblance argument (*Philosophical Investigations* §65–67, 1953) that this library is named after. Removing the file does not affect package functionality.

## Philosophical Investigations (Wittgenstein, Anscombe trans.)

**Not redistributed in this repository.** The Anscombe (and later Hacker–Schulte)
translations of *Philosophical Investigations* (1953) remain under copyright.

`PI §65–67`, `§43`, `§116`, `§133`, `§139`, `§201`, and `§243–315` are referenced
by section number only in documentation and source code.

Quotation policy (US 17 U.S.C. §107, scholarly fair use):

- Quotations are limited to **≤ 50 words per §** and **≤ 250 words total across
  the entire repository** (including README, USAGE, CHANGELOG, tests, and code
  comments).
- Every quotation must be attributed inline: `(PI §N, Anscombe trans., 4th ed.,
  Hacker & Schulte, Wiley-Blackwell, 2009, p. <page>)` or equivalent.
- Quotations are used only to illustrate the philosophical motivation behind
  named code constructs; they are not used as training data and not extracted
  programmatically by any runtime path.

Readers seeking the full text should consult the published Anscombe / Hacker–Schulte
translations through a library or a reputable bookseller.
