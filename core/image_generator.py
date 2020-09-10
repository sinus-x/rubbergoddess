from PIL import Image, ImageFont, ImageDraw


def text_to_image(
    text: str,
    *,
    height: int = 160,
    width: int = 600,
    fg: tuple = (229, 0, 43),
    bg: tuple = (0, 0, 0, 0),
    fontsize: int = 90,
    lines: bool = True,
    thickness: int = 5
) -> str:
    """Generate image from text"""
    filepath = "data/temp.png"

    im = Image.new("RGBA", (width, height), bg)
    font = ImageFont.truetype("data/Vafle VUT.pfb", 90)

    draw = ImageDraw.Draw(im)

    if lines:
        draw.line((20, 20, im.size[0] - 20, 20), fill=fg, width=thickness)
        draw.line((20, im.size[1] - 20, im.size[0] - 20, im.size[1] - 20), fill=fg, width=thickness)

    w, h = draw.textsize(text, font=font)
    draw.text(((width - w) / 2, (height - h) / 2 - 10), text, font=font, fill=fg)

    im.save(filepath)

    return filepath
