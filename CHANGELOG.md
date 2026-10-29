# Changelog

## 2026-07-07 — repository audit

- Repositioned README as a generic product image cropper rather than a brand-specific utility.
- Added generated-output ignores for `1524x2200/`, `output/`, `outputs/`, `dist/` and `build/`.
- Kept PyInstaller `.spec` files trackable as build metadata.
- No credentials observed in inspected current files.

## Current version

- Tkinter folder picker.
- Batch center crop/resize to `1524x2200`.
- ICC profile handling and sRGB conversion attempt.

## 2026-10-29

- Fixed ICC conversion: transform the original pixel mode and embed the destination sRGB profile.
- Do not retain an invalid source profile after fallback RGB conversion.
- Added dependency installation instructions and synthetic color-profile regression tests.
