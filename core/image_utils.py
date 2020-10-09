from PIL import Image, ImageFont, ImageDraw
import numpy as np


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


# Taken from https://stackoverflow.com/a/7274986
# unutbu, September 2011 (https://stackoverflow.com/users/190597/unutbu)
def rgb_to_hsv(rgb):
    # Translated from source of colorsys.rgb_to_hsv
    # r,g,b should be a numpy arrays with values between 0 and 255
    # rgb_to_hsv returns an array of floats between 0.0 and 1.0.
    rgb = rgb.astype("float")
    hsv = np.zeros_like(rgb)
    # in case an RGBA array was passed, just copy the A channel
    hsv[..., 3:] = rgb[..., 3:]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb[..., :3], axis=-1)
    minc = np.min(rgb[..., :3], axis=-1)
    hsv[..., 2] = maxc
    mask = maxc != minc
    hsv[mask, 1] = (maxc - minc)[mask] / maxc[mask]
    rc = np.zeros_like(r)
    gc = np.zeros_like(g)
    bc = np.zeros_like(b)
    rc[mask] = (maxc - r)[mask] / (maxc - minc)[mask]
    gc[mask] = (maxc - g)[mask] / (maxc - minc)[mask]
    bc[mask] = (maxc - b)[mask] / (maxc - minc)[mask]
    hsv[..., 0] = np.select([r == maxc, g == maxc], [bc - gc, 2.0 + rc - bc], default=4.0 + gc - rc)
    hsv[..., 0] = (hsv[..., 0] / 6.0) % 1.0
    return hsv


def hsv_to_rgb(hsv):
    # Translated from source of colorsys.hsv_to_rgb
    # h,s should be a numpy arrays with values between 0.0 and 1.0
    # v should be a numpy array with values between 0.0 and 255.0
    # hsv_to_rgb returns an array of uints between 0 and 255.
    rgb = np.empty_like(hsv)
    rgb[..., 3:] = hsv[..., 3:]
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = (h * 6.0).astype("uint8")
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    conditions = [s == 0.0, i == 1, i == 2, i == 3, i == 4, i == 5]
    rgb[..., 0] = np.select(conditions, [v, q, p, p, t, v], default=v)
    rgb[..., 1] = np.select(conditions, [v, v, v, q, p, p], default=t)
    rgb[..., 2] = np.select(conditions, [v, p, t, v, v, q], default=p)
    return rgb.astype("uint8")


def shift_hue(arr, hout):
    arr = np.array(arr)
    hsv = rgb_to_hsv(arr)
    hsv[..., 0] = hout
    rgb = hsv_to_rgb(hsv)
    return rgb
