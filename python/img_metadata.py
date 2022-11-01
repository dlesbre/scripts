#!/usr/bin/env python3

from sys import argv

from pathlib import Path
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS


def print_metadata1(image: Image):
    info_dict = {
        "Filename": image.filename,
        "Image Size": image.size,
        "Image Height": image.height,
        "Image Width": image.width,
        "Image Format": image.format,
        "Image Mode": image.mode,
        "Image is Animated": getattr(image, "is_animated", False),
        "Frames in Image": getattr(image, "n_frames", 1),
    }

    for label, value in info_dict.items():
        print(f"{label:25}: {repr(value)}  ({type(value)})")


def print_metadata2(image: Image):
    # extract EXIF data
    exifdata = image.getexif()
    # for attr, value in image.__dict__.items():
    # 	print(f"{attr:25}: {value}")
    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes
        if isinstance(data, bytes):
            data = data.decode()
        print(f"{tag:25}:  {repr(data)}  ({type(data)})")


def ensure_unique(filename: str):
    path = Path(filename)
    name = path.name  # remove leading directories
    suffix = path.suffix
    print(f"'{name}', '{suffix}'")


def img_date(fn):
    "returns the image date from image (if available)"
    std_fmt = "%Y:%m:%d %H:%M:%S"
    tags = [
        36867,  # DateTimeOriginal
        36868,  # DateTimeDigitized
        306,
    ]  # DateTime
    exif = fn._getexif()
    if exif is None:
        return
    for t in tags:
        dat = exif.get(t)

        # PIL.PILLOW_VERSION >= 3.0 returns a tuple
        dat = dat[0] if isinstance(dat, tuple) else dat
        if dat is not None:
            break

    if dat is None:
        return None
    T = datetime.strptime(dat, std_fmt)
    print(T, type(T))
    return T


if __name__ == "__main__":
    image = Image.open(argv[1])
    print("==== Basic Metadata =========================")
    print_metadata1(image)
    print("\n==== Advanced Metadata ======================")
    print_metadata2(image)
    ensure_unique(image.filename)
    img_date(image)
