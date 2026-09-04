#!/usr/bin/env python3
"""
Generates og-image.png (1200x630), twitter-card.png and apple-touch-icon.png
in the site root, drawn in the site's own design language: amber phosphor on
graphite, hairline frame, the vertical rail, and the ambiguity -> impact axis.

Run from anywhere:  python3 tools/make-assets.py
Requires Pillow only. Uses system fonts so it needs no network.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE, SURFACE = (14, 16, 17), (20, 23, 26)
LINE, LINE_SOFT = (37, 42, 46), (28, 32, 35)
TEXT, TEXT2 = (237, 234, 228), (180, 183, 179)
MUTED, FAINT = (131, 136, 138), (93, 98, 101)
ACCENT, ACCENT_HI = (229, 162, 68), (240, 184, 101)

SANS_CANDIDATES = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
SANS_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
MONO_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def pick(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise SystemExit("No usable font found in: %s" % paths)


SANS, SANS_B, MONO = pick(SANS_CANDIDATES), pick(SANS_BOLD_CANDIDATES), pick(MONO_CANDIDATES)
f_sans = lambda s: ImageFont.truetype(SANS, s)
f_bold = lambda s: ImageFont.truetype(SANS_B, s)
f_mono = lambda s: ImageFont.truetype(MONO, s)


def tw(d, text, font):
    """Text width, measured the way Pillow >=10 wants."""
    return d.textbbox((0, 0), text, font=font)[2]


def tracked(d, xy, text, font, fill, track=0.0):
    """Draw text with extra letter-spacing, for the mono eyebrow."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += tw(d, ch, font) + track
    return x


def mark(d, x, y, s):
    """Monogram: two offset brackets. Same language as favicon.svg."""
    t = max(2, int(s * 0.085))
    off = s * 0.13
    bx, by = x + s * 0.26, y + s * 0.22
    bw, bh = s * 0.40, s * 0.56
    for dx, dy, col in ((off, off, ACCENT), (0, 0, TEXT)):
        d.line([(bx + dx + bw, by + dy), (bx + dx, by + dy),
                (bx + dx, by + dy + bh)], fill=col, width=t, joint="curve")
        d.line([(bx + dx, by + dy + bh * 0.52),
                (bx + dx + bw * 0.72, by + dy + bh * 0.52)], fill=col, width=t)


def og():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), BASE)
    d = ImageDraw.Draw(im)

    d.rectangle([40, 40, W - 41, H - 41], outline=LINE, width=1)

    rail = 172
    d.line([(rail, 41), (rail, H - 41)], fill=LINE_SOFT, width=1)

    d.text((74, 98), "01", font=f_mono(15), fill=FAINT)
    d.text((74, 126), "lagos", font=f_mono(14), fill=FAINT)
    d.text((74, 148), "remote", font=f_mono(14), fill=FAINT)

    x = rail + 44

    # monogram sits top-right, clear of the type and the axis below it
    mark(d, W - 148, 78, 62)

    d.ellipse([x, 100, x + 9, 109], fill=ACCENT)
    tracked(d, (x + 22, 96), "PRODUCT MANAGER  ·  PRODUCT BUILDER",
            f_mono(16), ACCENT, track=0.9)

    d.text((x, 178), "I build products", font=f_bold(70), fill=TEXT)
    d.text((x, 258), "from ambiguity to impact.", font=f_bold(70), fill=TEXT)

    d.text((x, 350), "4+ years product management  ·  7+ years broader experience",
           font=f_sans(23), fill=TEXT2)

    # Axis motif. The headline already says ambiguity -> impact, so the diagram
    # labels the five surfaces instead of repeating it.
    ax, ay, aw, rise = x + 22, 470, W - x - 140, 56
    n = 5
    pts = [(ax + (aw / (n - 1)) * i, ay - (rise / (n - 1)) * i) for i in range(n)]
    d.line([(ax - 22, ay + 30), (ax + aw + 22, ay + 30)], fill=LINE_SOFT, width=1)

    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(edge).line(pts, fill=ACCENT + (135,), width=2, joint="curve")
    im.paste(Image.alpha_composite(im.convert("RGBA"), edge).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(im)

    labels = ["Business", "Product", "Technology", "Data", "Growth"]
    lab = f_mono(14)
    for i, (px, py) in enumerate(pts):
        r = 6.5
        d.ellipse([px - r, py - r, px + r, py + r], fill=BASE,
                  outline=ACCENT_HI if i == n - 1 else ACCENT, width=2)
        if i == n - 1:
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=ACCENT_HI)
        # labels alternate above/below the polyline so they never touch it
        ly = py - 30 if i % 2 else py + 18
        d.text((px - tw(d, labels[i], lab) / 2, ly), labels[i], font=lab, fill=MUTED)

    nm, fn = "Olamide Olanipekun", f_sans(22)
    d.text((x, H - 92), nm, font=fn, fill=TEXT)
    d.text((x + tw(d, nm, fn) + 18, H - 89), "Flux", font=f_mono(15), fill=FAINT)
    return im


def icon(size=180):
    im = Image.new("RGB", (size, size), BASE)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, size - 1, size - 1], outline=LINE, width=1)
    mark(d, size * 0.13, size * 0.13, size * 0.74)
    return im


if __name__ == "__main__":
    card = og()
    for name in ("og-image.png", "twitter-card.png"):
        card.save(os.path.join(ROOT, name), optimize=True)
    icon(180).save(os.path.join(ROOT, "apple-touch-icon.png"), optimize=True)
    print("Wrote og-image.png, twitter-card.png, apple-touch-icon.png to", ROOT)
