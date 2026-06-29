"""Regenerate the logo deliverable set from the editable master.

From ``logo-fiberpath.svg`` (the hand-tuned mark, with live text), produces the
mark plus both lockups, each transparent + white, as SVG + PNG. Text is outlined
so the outputs carry no font dependency. The wordmark is set in DejaVu Sans Mono
Bold to match the binary in the mark.

Requires Inkscape on PATH. Run:  python build.py
"""

from __future__ import annotations

import pathlib
import re
import subprocess

INK = "#090909"
HERE = pathlib.Path(__file__).parent
NS = ('xmlns="http://www.w3.org/2000/svg" '
      'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
      'xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"')


def _inkscape(*args: str) -> None:
    subprocess.run(("inkscape", *args), check=True, capture_output=True)


def _path(name: str) -> str:
    return str(HERE / name)


def _read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8")


def _write(name: str, text: str) -> None:
    (HERE / name).write_text(text, encoding="utf-8")


def _svg_inner(text: str) -> str:
    """Strip the outer <svg> wrapper, XML decl, and Inkscape namedview."""
    text = re.sub(r"<\?xml[^>]*\?>", "", text)
    text = re.sub(r"<svg\b[^>]*?>", "", text, count=1, flags=re.S).replace("</svg>", "")
    text = re.sub(r"<sodipodi:namedview\b.*?(/>|</sodipodi:namedview>)", "", text, flags=re.S)
    return text.strip()


def _outline_mark() -> tuple[str, float, float]:
    """Outline the master's text, drop its white bg, tight-crop. Returns the
    transparent mark's inner SVG and its (width, height)."""
    _inkscape(_path("logo-fiberpath.svg"), "--export-text-to-path", "--export-type=svg",
              f"--export-filename={_path('_outlined.svg')}")
    outlined = re.sub(r'<rect\b[^>]*\bid="rect1"[^>]*/>', "", _read("_outlined.svg"),
                      count=1, flags=re.S)
    _write("mark.svg", outlined)
    _inkscape(_path("mark.svg"), "--export-area-drawing", "--export-type=svg",
              f"--export-filename={_path('mark-tight.svg')}")
    tight = _read("mark-tight.svg")
    mw, mh = (float(v) for v in re.search(r'viewBox="0 0 (\S+) (\S+)"', tight).groups())
    return _svg_inner(tight), mw, mh


def _outline_wordmark() -> tuple[str, tuple[float, float, float, float]]:
    """Outline 'FiberPath'. Returns the path data and its (x, y, w, h) bbox."""
    _write("_wm.svg",
           '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="200" '
           'viewBox="0 0 900 200">'
           f'<text x="0" y="150" font-family="\'DejaVu Sans Mono\'" font-weight="bold" '
           f'font-size="130" fill="{INK}">FiberPath</text></svg>')
    _inkscape(_path("_wm.svg"), "--export-text-to-path", "--export-type=svg",
              f"--export-filename={_path('_wm_out.svg')}")
    query = subprocess.run(("inkscape", _path("_wm_out.svg"), "--query-all"),
                           capture_output=True, text=True).stdout
    bbox = tuple(float(v) for v in query.splitlines()[0].split(",")[1:5])
    path_d = re.search(r'<path[^>]*\bd="([^"]+)"', _read("_wm_out.svg"), re.S).group(1)
    return path_d, bbox


def main() -> None:
    mark_inner, mw, mh = _outline_mark()
    wm_d, (wbx, wby, wbw, wbh) = _outline_wordmark()

    def mark_block(x: float, y: float) -> str:
        return (f'<svg x="{x:.3f}" y="{y:.3f}" width="{mw:.3f}" height="{mh:.3f}" '
                f'viewBox="0 0 {mw} {mh}" overflow="visible">\n{mark_inner}\n</svg>')

    def wm_block(x: float, y: float, scale: float) -> str:
        tx, ty = x - wbx * scale, y - wby * scale
        return (f'<g transform="translate({tx:.3f},{ty:.3f}) scale({scale})">'
                f'<path d="{wm_d}" fill="{INK}"/></g>')

    def write_lockup(name: str, w: float, h: float, body: str) -> None:
        _write(name, f'<svg {NS} viewBox="0 0 {w:.3f} {h:.3f}" '
                     f'width="{w:.3f}" height="{h:.3f}">\n{body}\n</svg>\n')

    # stacked: mark over centred wordmark
    pad, gap, scale = 40.0, 64.0, 1.0
    ww, wh = wbw * scale, wbh * scale
    cw, ch = max(mw, ww) + 2 * pad, pad + mh + gap + wh + pad
    write_lockup("lockup-stacked.svg", cw, ch,
                 mark_block((cw - mw) / 2, pad) + "\n"
                 + wm_block((cw - ww) / 2, pad + mh + gap, scale))

    # horizontal: mark left, wordmark right (vertically centred, larger)
    pad, gap, scale = 40.0, 80.0, 1.5
    ww, wh = wbw * scale, wbh * scale
    ch, cw = pad + mh + pad, pad + mw + gap + ww + pad
    write_lockup("lockup-horizontal.svg", cw, ch,
                 mark_block(pad, (ch - mh) / 2) + "\n"
                 + wm_block(pad + mw + gap, ch / 2 - wh / 2, scale))

    # white-background and reversed (white-ink) SVG variants
    for src in ("mark.svg", "lockup-stacked.svg", "lockup-horizontal.svg"):
        text = _read(src)
        w, h = re.search(r'viewBox="0 0 (\S+) (\S+)"', text).groups()
        rect = f'\n  <rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>'
        _write(src.replace(".svg", "-white.svg"),
               re.sub(r"(<svg\b[^>]*?>)", r"\1" + rect, text, count=1, flags=re.S))
        _write(src.replace(".svg", "-reversed.svg"), text.replace(INK, "#ffffff"))

    # PNGs at deploy resolution: transparent, white bg, and reversed (for dark bg)
    for src, width in (("mark.svg", 1024), ("lockup-stacked.svg", 1600),
                       ("lockup-horizontal.svg", 2400)):
        base = src[:-4]
        _inkscape(_path(src), "--export-type=png",
                  f"--export-filename={_path(base + '.png')}", f"--export-width={width}")
        _inkscape(_path(src), "--export-type=png",
                  f"--export-filename={_path(base + '-white.png')}", f"--export-width={width}",
                  "--export-background=#ffffff", "--export-background-opacity=1")
        _inkscape(_path(base + "-reversed.svg"), "--export-type=png",
                  f"--export-filename={_path(base + '-reversed.png')}", f"--export-width={width}")

    for tmp in ("_outlined.svg", "mark-tight.svg", "_wm.svg", "_wm_out.svg"):
        (HERE / tmp).unlink(missing_ok=True)
    print(f"build complete; ink {INK}  mark {mw:.0f}x{mh:.0f}  wordmark {wbw:.0f}x{wbh:.0f}")


if __name__ == "__main__":
    main()
