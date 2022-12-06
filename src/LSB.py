from typing import List, Literal
from os.path import exist
from os import listdir 
from pathlib import Path 
from argparse import ArgumentParser, Namespace

import numpy as np
from PIL import Image


def encode(img: Image.Image, msg: str, signature: str = '$t3g0') -> Image.Image:
    """Embed hidden message on an image

    Args:
        img (Image.Image): Image with secret message
        msg (str): Hidden message to be embedded
        signature (str, optional): Unique signature of the message. Defaults to ''.

    Raises:
        ValueError: When the size of bytes is more than `pixel_size`

    Returns:
        Image.Image: Encoded image
    """
    _w, _h = img.size 
    pixels = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n:Literal[3] = 3
    else:
        n:Literal[4] = 4
    
    pixel_size = pixels.size // n 
    encoded_msg = f'{msg} {signature}'
    byte_msg = ''.join(format(ord(i), '08b') for i in encoded_msg) 
    req_pixels = len(byte_msg)

    if req_pixels > pixel_size:
        raise ValueError()
    else: 
        index:Literal[0] = 0 
        for x in range(pixel_size):
            for y in range(n):
                if index < req_pixels: 
                    pixels[x][y] = int(bin(pixels[x][y])[2:9] + byte_msg[index], 2)
                    index += 1
        pixels = pixels.reshape(_h, _w, n)
        return Image.fromarray(pixels.astype('uint8'), img.mode)

def decode(img:Image.Image) -> str:
    """Finds the hidden message in the image

    Args:
        img (Image.Image): _description_

    Returns:
        str: _description_
    """
    pixels = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n:Literal[3] = 3
    else: 
        n:Literal[4] = 4

    pixel_size = pixels.size // n
    hidden_bits = ''
    decoded_msg = ''
    
    for x in range(pixel_size): 
        for y in range(3):
            hidden_bits += (bin(pixels[x][y])[2:][-1])

    hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]
    for i in range(len(hidden_bits)):
        if decoded_msg[-5:] == '$t3g0':
            break
        else:
            decoded_msg += chr(int(hidden_bits[i], 2))

    if '$t3g0' in decoded_msg: 
        return decoded_msg
    return 'no hidden message found'

def find_img(img_path:Path) -> List[Path]:
    """Finds image path

    Args:
        img_path (Path): Base path to explore

    Raises:
        ValueError: If `img_path` is not a valid directory

    Returns:
        List[Path]: List of image paths that ends with '.jpg' or '.png'
    """
    if not exist(img_path):
        raise ValueError(f'Invalid path: {img_path}')
    return [
        f_name/img_path for f_name in listdir(img_path) if f_name.endswith(('.jpg','.png'))
    ]

if __name__ == '__main__':
    parser = ArgumentParser(
        decription='Hide Message to Image in -inpath and stores it to -outpath'
    )

    parser.add_argument(
        '-inpath', metavar='inpath', type=Path, help='input path for set of images to be encoded'
    )

    parser.add_argument(
        '-outpath', metavar='outpath', type=Path, help='output path for set of encoded images to be stored'
    )

    parser.add_argument(
        '-encode_message', metavar='encoded_msg', type=str, help='Message to be encoded in the image'
    )

    rel_path:Path = Path.home()/'Downloads'/'Steno'
    img_path:Path = rel_path/'SampleImages'/'BabyBear.jpg'

    img = Image.open(img_path).convert('RGB')
    enc_img = encode(img, 'secret message hidden in the image')
    
    enc_img.save(rel_path/'EncodedImages'/img_path.name)
    print(decode(enc_img))
