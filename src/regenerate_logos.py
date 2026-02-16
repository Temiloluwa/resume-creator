#!/usr/bin/env python3
"""Generate transparent PNG logos for resume rendering."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "data" / "logos"
SIZE = (160, 160)


try:
    FONT_BOLD = ImageFont.truetype("Arial Bold.ttf", 52)
    FONT_MED = ImageFont.truetype("Arial.ttf", 24)
except OSError:
    FONT_BOLD = ImageFont.load_default()
    FONT_MED = ImageFont.load_default()


def base() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def centered(draw: ImageDraw.ImageDraw, text: str, y: int, fill: tuple[int, int, int, int], font: ImageFont.ImageFont) -> None:
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw.text(((SIZE[0] - (x1 - x0)) / 2, y), text, font=font, fill=fill)


def save(name: str, draw_fn) -> None:
    im, draw = base()
    draw_fn(draw)
    im.save(OUT / name)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    save("yougov.png", lambda d: (
        d.ellipse((18, 18, 142, 142), outline=(28, 50, 115, 255), width=6),
        centered(d, "YG", 48, (28, 50, 115, 255), FONT_BOLD),
    ))

    save("reply.png", lambda d: (
        d.rounded_rectangle((12, 12, 148, 148), radius=22, outline=(0, 0, 0, 255), width=6),
        centered(d, "R", 44, (0, 0, 0, 255), FONT_BOLD),
        centered(d, "Reply", 108, (0, 0, 0, 220), FONT_MED),
    ))

    save("fraunhofer.png", lambda d: (
        d.polygon([(24, 120), (80, 24), (136, 120)], outline=(0, 122, 83, 255), width=6),
        centered(d, "F", 60, (0, 122, 83, 255), FONT_BOLD),
    ))

    save("slb.png", lambda d: (
        d.arc((18, 18, 142, 142), start=210, end=330, fill=(190, 26, 37, 255), width=7),
        d.arc((18, 18, 142, 142), start=30, end=150, fill=(190, 26, 37, 255), width=7),
        centered(d, "SLB", 52, (190, 26, 37, 255), FONT_BOLD),
    ))

    save("hildesheim.png", lambda d: (
        d.rectangle((20, 20, 140, 140), outline=(0, 67, 148, 255), width=6),
        centered(d, "UH", 50, (0, 67, 148, 255), FONT_BOLD),
    ))

    save("ibadan.png", lambda d: (
        d.rectangle((20, 20, 140, 140), outline=(123, 30, 44, 255), width=6),
        centered(d, "UI", 50, (123, 30, 44, 255), FONT_BOLD),
    ))

    save("redi.png", lambda d: (
        d.rounded_rectangle((18, 18, 142, 142), radius=24, outline=(222, 58, 31, 255), width=6),
        centered(d, "ReDI", 64, (222, 58, 31, 255), FONT_MED),
    ))

    save("aws.png", lambda d: (
        centered(d, "aws", 54, (255, 153, 0, 255), FONT_BOLD),
        d.arc((42, 94, 118, 140), start=200, end=340, fill=(255, 153, 0, 255), width=5),
    ))

    save("deeplearning.png", lambda d: (
        d.ellipse((20, 20, 140, 140), outline=(0, 87, 184, 255), width=6),
        centered(d, "DL", 50, (0, 87, 184, 255), FONT_BOLD),
        centered(d, "AI", 100, (0, 87, 184, 230), FONT_MED),
    ))

    print("regenerated transparent logos")


if __name__ == "__main__":
    main()
