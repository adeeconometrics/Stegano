from typing import (Literal, Dict,
                    Callable, Union, Optional)
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
    assert isinstance(img, Image.Image)
    _w, _h = img.size
    pixels = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n: Literal[3] = 3
    else:
        n: Literal[4] = 4

    pixel_size = pixels.size // n
    encoded_msg = f'{msg}{signature}'
    byte_msg = ''.join(format(ord(i), '08b') for i in encoded_msg)
    req_pixels = len(byte_msg)

    if req_pixels > pixel_size:
        raise ValueError()
    else:
        index: Literal[0] = 0
        for x in range(pixel_size):
            for y in range(n):
                if index < req_pixels:
                    pixels[x][y] = int(bin(pixels[x][y])[
                                       2:9] + byte_msg[index], 2)
                    index += 1
        pixels = pixels.reshape(_h, _w, n)
        return Image.fromarray(pixels.astype('uint8'), img.mode)


def decode(img: Image.Image, signature: str = '$t3g0') -> str:
    """Finds the hidden message in the image

    Args:
        img (Image.Image): _description_

    Returns:
        str: _description_
    """
    assert isinstance(img, Image.Image)

    pixels = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n: Literal[3] = 3
    else:
        n: Literal[4] = 4

    pixel_size = pixels.size // n
    hidden_bits = ''
    decoded_msg = ''

    for x in range(pixel_size):
        for y in range(3):
            hidden_bits += (bin(pixels[x][y])[2:][-1])

    hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]
    for i in range(len(hidden_bits)):
        if decoded_msg[-len(signature):] == signature:
            break
        decoded_msg += chr(int(hidden_bits[i], 2))

    if signature in decoded_msg:
        return decoded_msg.replace(signature, '')
    return 'no hidden message found'


if __name__ == '__main__':
    interface: Dict[str, Union[
        Callable[[Image.Image, str, str], Image.Image],
        Callable[[Image.Image, str], str]]] = {
            'encode': encode,
            'decode': decode
    }

    parser = ArgumentParser(
        description='Hide Message to Image in -inpath and stores it to -outpath'
    )

    parser.add_argument(
        '-o', '-outpath', metavar='outpath', 
        type=Path, help='output path for set of encoded images to be stored'
    )
    parser.set_defaults(outpath=Path.cwd()/'EncodedImages')
    parser.add_argument(
        '-type', choices=list(interface.keys())
    )
    parser.add_argument(
        '-arguments', nargs='+'
    )

    def encode_types(a: Path, b: str, c: Optional[str] = None) -> tuple:
        if c is not None:
            return Image.open(a), b, c
        return Image.open(a), b

    def decode_types(a: Path, b: str = '$t3g0') -> tuple:
        return Image.open(a), b


    args: Namespace = parser.parse_args()

    if args.type =='encode':
        arguments = encode_types(*args.arguments)
        interface[args.type](*arguments).save(args.outpath/'LSBBabyBear.jpg')
        print('encoded')
    elif args.type == 'decode':
        arguments = decode_types(*args.arguments)
        print(interface[args.type](*arguments))

    print(args)