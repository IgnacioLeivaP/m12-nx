"""Convierte un .TDX de PC (DXT1/DXT3/DXT5 o BGRA de 32 bits, formato 21) de
Duels of the Planeswalkers a PNG.

    py -I tdx2png.py fichero.TDX salida.png

Cabecera de 16 bytes: u16 ?, u16 ancho (+2), u16 alto (+4), ..., formato FourCC
en +0xc ("DXT1", "DXT3", "DXT5"); detras, el primer nivel comprimido (y sus
mipmaps). Se envuelve en un DDS minimo y lo decodifica Pillow.
"""
import io
import struct
import sys

from PIL import Image


def tdx_to_image(data):
    width, height = struct.unpack_from('<HH', data, 2)
    fourcc = data[12:16]
    if fourcc in (struct.pack('<I', 21), struct.pack('<I', 22)):  # D3DFMT_A8R8G8B8 / X8R8G8B8
        raw = data[16:16 + width * height * 4]
        if fourcc[0] == 21:
            return Image.frombuffer('RGBA', (width, height), raw, 'raw', 'BGRA', 0, 1)
        return Image.frombuffer('RGB', (width, height), raw, 'raw', 'BGRX', 0, 1).convert('RGBA')
    if fourcc == struct.pack('<I', 0x12):  # iPad: RGBA8888 sin comprimir
        raw = data[16:16 + width * height * 4]
        return Image.frombuffer('RGBA', (width, height), raw, 'raw', 'RGBA', 0, 1)
    if fourcc == struct.pack('<I', 0x13):  # iPad: RGB565 sin comprimir
        raw = data[16:16 + width * height * 2]
        return Image.frombuffer('RGB', (width, height), raw, 'raw', 'BGR;16', 0, 1).convert('RGBA')
    if fourcc not in (b'DXT1', b'DXT3', b'DXT5'):
        raise ValueError(f'formato no soportado: {fourcc!r}')
    block = 8 if fourcc == b'DXT1' else 16
    size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * block
    pixels = data[16:16 + size]
    if len(pixels) < size:
        raise ValueError('el fichero es mas corto que el primer nivel')
    header = struct.pack(
        '<4s7I44x2I4s5I5I',
        b'DDS ', 124, 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000, height, width, size, 0, 1,
        32, 0x4, fourcc, 0, 0, 0, 0, 0,
        0x1000, 0, 0, 0, 0,
    )
    return Image.open(io.BytesIO(header + pixels)).convert('RGBA')


if __name__ == '__main__':
    image = tdx_to_image(open(sys.argv[1], 'rb').read())
    image.save(sys.argv[2])
    print(f'{sys.argv[2]}: {image.width}x{image.height}')
