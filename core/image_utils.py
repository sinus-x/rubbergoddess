from PIL import Image, ImageFont, ImageDraw
from typing import Tuple, List, Union
import numpy as np
from collections import defaultdict
from random import randrange
from itertools import chain


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
    font = ImageFont.truetype("resources/Vafle VUT.pfb", 90)

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


class GifConverter:
    # Sourced from https://gist.github.com/egocarib/ea022799cca8a102d14c54a22c45efe0
    _PALETTE_SLOTSET = set(range(256))

    def __init__(self, img_rgba: Image.Image, alpha_treshold: int = 0):
        self._img_rgba = img_rgba
        self._alpha_treshold = alpha_treshold

    def _process_pixels(self):
        """Set transparent pixels to the color palette index 0."""
        self._transparent_pixels = set(
            idx
            for idx, alpha in enumerate(self._img_rgba.getchannel(channel="A").getdata())
            if alpha <= self._alpha_treshold
        )

    def _set_parsed_palette(self):
        """Parse the RGB palette color `tuple`s from the palette."""
        palette = self._img_p.getpalette()
        self._img_p_used_palette_idxs = set(
            idx
            for pal_idx, idx in enumerate(self._img_p_data)
            if pal_idx not in self._transparent_pixels
        )
        self._img_p_parsedpalette = dict(
            (idx, tuple(palette[idx * 3 : idx * 3 + 3])) for idx in self._img_p_used_palette_idxs
        )

    def _get_similar_color_idx(self):
        """Return a palette index with the closest similar color."""
        old_color = self._img_p_parsedpalette[0]
        dict_distance = defaultdict(list)
        for idx in range(1, 256):
            color_item = self._img_p_parsedpalette[idx]
            if color_item == old_color:
                return idx
            distance = sum(
                (
                    abs(old_color[0] - color_item[0]),  # Red
                    abs(old_color[1] - color_item[1]),  # Green
                    abs(old_color[2] - color_item[2]),  # Blue
                )
            )
            dict_distance[distance].append(idx)
        return dict_distance[sorted(dict_distance)[0]][0]

    def _remap_palette_idx_zero(self):
        """Since the first color is used in the palette, remap it."""
        free_slots = self._PALETTE_SLOTSET - self._img_p_used_palette_idxs
        new_idx = free_slots.pop() if free_slots else self._get_similar_color_idx()
        self._img_p_used_palette_idxs.add(new_idx)
        self._palette_replaces["idx_from"].append(0)
        self._palette_replaces["idx_to"].append(new_idx)
        self._img_p_parsedpalette[new_idx] = self._img_p_parsedpalette[0]
        del self._img_p_parsedpalette[0]

    def _get_unused_color(self) -> tuple:
        """Return a color for the palette that does not collide with any other
        already in the palette."""
        used_colors = set(self._img_p_parsedpalette.values())
        while True:
            new_color = (randrange(256), randrange(256), randrange(256))
            if new_color not in used_colors:
                return new_color

    def _process_palette(self):
        """Adjust palette to have the zeroth color set as transparent.
        Basically, get another palette index for the zeroth color."""
        self._set_parsed_palette()
        if 0 in self._img_p_used_palette_idxs:
            self._remap_palette_idx_zero()
        self._img_p_parsedpalette[0] = self._get_unused_color()

    def _adjust_pixels(self):
        """Convert the pixels into their new values."""
        if self._palette_replaces["idx_from"]:
            trans_table = bytearray.maketrans(
                bytes(self._palette_replaces["idx_from"]), bytes(self._palette_replaces["idx_to"])
            )
            self._img_p_data = self._img_p_data.translate(trans_table)
        for idx_pixel in self._transparent_pixels:
            self._img_p_data[idx_pixel] = 0
        self._img_p.frombytes(data=bytes(self._img_p_data))

    def _adjust_palette(self):
        """Modify the palette in the new `Image`."""
        unused_color = self._get_unused_color()
        final_palette = chain.from_iterable(
            self._img_p_parsedpalette.get(x, unused_color) for x in range(256)
        )
        self._img_p.putpalette(data=final_palette)

    def process(self) -> Image.Image:
        """Return the processed mode `P` `Image`."""
        self._img_p = self._img_rgba.convert(mode="P")
        self._img_p_data = bytearray(self._img_p.tobytes())
        self._palette_replaces = dict(idx_from=list(), idx_to=list())
        self._process_pixels()
        self._process_palette()
        self._adjust_pixels()
        self._adjust_palette()
        self._img_p.info["transparency"] = 0
        self._img_p.info["background"] = 0
        return self._img_p


def create_animated_gif(
    images: List[Image.Image], duration: Union[int, List[int]]
) -> Tuple[Image.Image, dict]:
    """If the image is a GIF, create an its thumbnail here."""
    save_kwargs = dict()
    new_images: List[Image] = []

    for frame in images:
        thumbnail: Image.Image = frame.copy()
        thumbnail_rgba = thumbnail.convert(mode="RGBA")
        thumbnail_rgba.thumbnail(size=frame.size, reducing_gap=3.0)
        converter = GifConverter(img_rgba=thumbnail_rgba)
        thumbnail_p = converter.process()  # type: Image
        new_images.append(thumbnail_p)

    output_image = new_images[0]
    save_kwargs.update(
        format="GIF",
        save_all=True,
        optimize=False,
        append_images=new_images[1:],
        duration=duration,
        disposal=2,  # Other disposals don't work
        loop=0,
    )
    return output_image, save_kwargs


def save_gif(images: List[Image.Image], duration: Union[int, List[int]], save_file: str):
    """Create a transparent GIF, with no problems with transparent pixel flashing

    Does not work with partial alpha, which gets discarded and replaced by solid colors.

    Parameters:
      images: list of Pillow Image objects that compose the GIF frames
      durations: an int or list of ints that describe the frame durations
      save_file: A string, pathlib.Path or file object to save the file to.
    """
    root_frame, save_args = create_animated_gif(images, duration)
    root_frame.save(save_file, **save_args)
