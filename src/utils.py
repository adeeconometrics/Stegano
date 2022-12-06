from typing import List
from pathlib import Path
from os.path import exists
from os import listdir

from PIL import Image


def find_imgs(img_path: Path) -> List[Path]:
    """Finds image path

    Args:
        img_path (Path): Base path to explore

    Raises:
        ValueError: If `img_path` is not a valid directory

    Returns:
        List[Path]: List of image paths that ends with '.jpg' or '.png'
    """
    if not exists(img_path):
        raise ValueError(f'Invalid path: {img_path}')
    return [
        f_name/img_path for f_name in listdir(img_path) if f_name.endswith(('.jpg', '.png'))
    ]

def read_img(img_path:Path) -> Image.Image:
    """Read image as RGB

    Args:
        img_path (Path): Image path

    Returns:
        Image.Image: PIL.Image.Image representation
    """
    return Image.open(img_path).convert('RGB')