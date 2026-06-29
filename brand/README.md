# FiberPath brand assets

**This directory is the single source of truth for FiberPath's logo and marks.**
Everything else (app icons, README banners, the docs favicon) is *derived* from
here — regenerate, don't hand-edit, and copy the few build assets each consumer
needs.

Mono, single ink **`#090909`**. All SVGs have outlined text (no font
dependency). Transparent variants have no background and the cylinder mouth is
open (transparent). Prefer SVG; the PNGs are 1024/1600/2400 px raster masters.

## Files

| Asset | Variants | Use |
|-------|----------|-----|
| `mark` | `.svg`/`.png`, `-white`, `-reversed` | The logo mark (cylinder + binary + toolpath). Large contexts, avatars. |
| `lockup-horizontal` | `.svg`/`.png`, `-white`, `-reversed` | Mark + wordmark side by side. README / page headers, banners. |
| `lockup-stacked` | `.svg`/`.png`, `-white`, `-reversed` | Mark over wordmark. Square-ish headers, social cards. |
| `icon` | `.svg`/`.png` | Simplified square mark (bold, no binary) — app icon / favicon source. |
| `logo-fiberpath.svg` | — | Editable master of the mark (live text, white bg). **Edit this, then regenerate.** |

`-white` = white background · `-reversed` = white ink (for dark backgrounds).

## Regenerate

Requires Inkscape (text outlining + PNG export).

```sh
python3 build.py      # mark + both lockups: transparent / white / reversed, SVG + PNG
python3 gen_icon.py   # icon.svg
inkscape icon.svg --export-type=png --export-filename=icon.png --export-width=1024
```

## Where the assets are consumed

Each repo vendors only the few derived files it builds/displays with, copied
from here. They are derived, so they don't drift in practice — if one ever
diverges, regenerate and re-copy.

| Repo | Needs | From |
|------|-------|------|
| `fiberpath/fiberpath` | `fiberpath_gui/src-tauri/icons/*` (app icons) + README banner | `icon.png` → `tauri icon`; `lockup-horizontal{,-reversed}.png` |
| `fiberpath/fiberpath.github.io` | docs logo + favicon | `icon.svg` → `docs/assets/logo.svg`; `icon` → `favicon` |
| this repo (`.github`) | org profile banner | `lockup-horizontal{,-reversed}.png` |

App icons (Tauri) are generated from `icon.png`:

```sh
cd fiberpath_gui && ./node_modules/.bin/tauri icon ../../.github/brand/icon.png
# desktop-only: delete the android/ ios/ subfolders it creates
```
