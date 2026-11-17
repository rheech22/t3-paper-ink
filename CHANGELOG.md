# Changelog

## Unreleased

- The design preview gains a Question screen with an interactive sticky-note question card, and the README shows it.

## 0.1.2 — 2026-11-18

- Pending question cards above the composer now look like a pale yellow sticky note with an ink border. Other notices keep the paper look.
- The composer casts a square ink shadow that follows its folded corner and any attached card, replacing the faint soft shadow.

Verified with a reproduction built from the compiled styles and component classes of T3 Code **0.1.10-nightly.20261114.4709**.

## 0.1.1 — 2026-11-18

- Fix the composer layout while a question card is attached. The white paper and folded corner now sit on the input surface instead of behind the whole card, and the input covers the bottom of the card again.
- Square the corners of question and notice cards above the composer to match the rest of the theme.

Verified with a reproduction built from the compiled styles and component classes of T3 Code **0.1.10-nightly.20261114.4709**.

## 0.1.0 — 2026-11-15

Initial public release.

- Warm paper surfaces, mint grain, and ink typography.
- Paper message cards and a folded white composer.
- Square controls with consistent selection and focus states.
- Contrast improvements for links, status labels, and settings text.
- A portable theme JSON, editable sources, and a dependency-free build script.
- An interactive design simulation and preview images with fictional content.

Initially checked against T3 Code **0.1.10-nightly.20261114.4709**.
Web and desktop, light appearance only. Custom CSS support is required.
