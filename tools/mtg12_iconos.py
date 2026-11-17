#!/usr/bin/env python3
"""Dibuja las variantes de iconos de botones (PlayStation y Switch) de Magic 2012.

Los iconos de Xbox que trae el juego se sustituyen por dibujos propios de este repositorio: formas geometricas y
letras hechas aqui, sin arte de terceros ni fuentes del sistema (mejor: nada que no se pueda redistribuir).

    py -3 tools/mtg12_iconos.py --data <carpeta_del_juego> --out <carpeta_de_salida>

Entrada: la carpeta del juego preparada por el instalador, con Data_Core.wad y Update001.wad (los del usuario).
Salida:  <out>/mtg12_buttons_ps.bin y <out>/mtg12_buttons_switch.bin: Update001.wad con las texturas cambiadas. El
         SDK redirige Update001.wad a la variante que elige el jugador, por eso van en la carpeta de datos del juego.

TDX (2012, Xbox): cabecera de 16 bytes en little endian (u16 0x0200, ancho, alto, niveles, u32 banderas, u32 formato)
y los pixeles en lineal; formato 21 = BGRA de 32 bits. Se convierten las texturas de 64x64, incluidas las variantes grises, y las hojas
SYMBOLS/SYMBOLS_FE (1024x1024, 11 niveles): los brillos quedan como estan.
Las hojas conservan sus 11 niveles y el bloque adicional original que va tras la cabecera; los niveles de 1024 a 32
se rehacen y la cola empaquetada menor de 32 se conserva.
"""
import argparse
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wad12  # noqa: E402

TEX = 'DATA_ALL_PLATFORMS/DATA_REQUIRED/LUBE/SKIND12/TEXTURES'
TEX360 = 'DATA_X360/DATA_SHARED/ART_ASSETS/TEXTURES'
SYMBOLS = 'DATA_X360/DATA_SHARED/ART_ASSETS/FONTS/SYMBOLS.TDX'

# Casillas de los botones de Xbox en SYMBOLS.TDX (y0, x0, y1, x1), en la hoja de 1024x1024 (rejilla de 84 pixeles).
CASILLAS = {
    'A': (598, 178, 658, 242), 'B': (598, 262, 658, 326),
    'X': (598, 346, 658, 410), 'Y': (598, 430, 658, 494),
    'LB': (514, 848, 578, 916), 'RB': (514, 932, 578, 1000),
    'LT': (598, 8, 662, 76), 'RT': (598, 92, 662, 160),
    'BACK': (598, 596, 662, 664), 'START': (598, 680, 662, 748),
}

# Colores de los dibujos (formas y letras propias, no una copia de ningun glifo).
AZUL = (58, 106, 200, 255)
ROJO = (206, 60, 60, 255)
ROSA = (216, 96, 176, 255)
VERDE = (66, 172, 96, 255)
GRIS = (86, 92, 104, 255)
CLARO = (240, 242, 246, 255)
OSCURO = (34, 38, 44, 255)


def leer_tdx(d):
    """(imagen, niveles, banderas, formato) de un TDX formato 21."""
    _, w, h, niveles, banderas, fmt = struct.unpack_from('<HHHHII', d, 0)
    if fmt != 21:
        import tdx2png
        return tdx2png.tdx_to_image(d).convert('RGBA'), niveles, banderas, fmt
    offset = 20 + struct.unpack_from('<I', d, 16)[0] if niveles > 1 else 16
    im = Image.frombuffer('RGBA', (w, h), d[offset:offset + w * h * 4], 'raw', 'BGRA', 0, 1).copy()
    return im, niveles, banderas, fmt


def escribir_tdx(im, banderas=0x5C8):
    im = im.convert('RGBA')
    return struct.pack('<HHHHII', 0x0200, im.width, im.height, 1, banderas, 21) + im.tobytes('raw', 'BGRA')


def _fuente(alto):
    """Una fuente de mapa de bits de PIL, ampliada al tamano pedido (sin ficheros de fuente del sistema)."""
    return ImageFont.load_default()


def texto(txt, ancho, alto, color):
    """El texto, lo mayor que entra en ancho x alto, centrado en un lienzo de ese tamano."""
    f = _fuente(alto)
    lienzo = Image.new('RGBA', (max(1, ancho), max(1, alto)), (0, 0, 0, 0))
    caja = f.getbbox(txt)
    tw, th = caja[2] - caja[0], caja[3] - caja[1]
    if tw <= 0 or th <= 0:
        return lienzo
    # Se dibuja pequeno y se amplia: el resultado queda suave y no depende de una fuente externa.
    base = Image.new('RGBA', (tw + 2, th + 2), (0, 0, 0, 0))
    ImageDraw.Draw(base).text((1 - caja[0], 1 - caja[1]), txt, font=f, fill=color)
    f2 = min(ancho / base.width, alto / base.height)
    nuevo = base.resize((max(1, round(base.width * f2)), max(1, round(base.height * f2))), Image.LANCZOS)
    lienzo.alpha_composite(nuevo, ((ancho - nuevo.width) // 2, (alto - nuevo.height) // 2))
    return lienzo


def forma(tipo, ancho, alto, color):
    """Un dibujo propio de la forma pedida, lo mayor que entra en ancho x alto."""
    esc = 4  # se dibuja grande y se reduce: bordes suaves
    W, H = max(1, ancho) * esc, max(1, alto) * esc
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    g = max(2, min(W, H) // 10)
    if tipo == 'cruz':
        w = max(2, (W - 2 * g) // 3)
        d.rectangle((W // 2 - w // 2, g, W // 2 + w // 2, H - g), fill=color)
        d.rectangle((g, H // 2 - w // 2, W - g, H // 2 + w // 2), fill=color)
    elif tipo == 'circulo':
        d.ellipse((g, g, W - g, H - g), outline=color, width=max(2, (W - 2 * g) // 6))
    elif tipo == 'cuadrado':
        d.rectangle((g, g, W - g, H - g), outline=color, width=max(2, (W - 2 * g) // 6))
    elif tipo == 'triangulo':
        d.polygon([(W // 2, g), (W - g, H - g), (g, H - g)], outline=color, width=max(2, (W - 2 * g) // 6))
    elif tipo == 'redondo':  # el fondo de una tecla: se lee igual sobre menus claros y oscuros
        d.ellipse((0, 0, W - 1, H - 1), fill=color)
    elif tipo == 'pastilla':
        d.rounded_rectangle((0, 0, W - 1, H - 1), radius=max(2, H // 3), fill=color)
    return im.resize((max(1, ancho), max(1, alto)), Image.LANCZOS)


def tecla(txt, ancho, alto, letra=CLARO, fondo=GRIS, forma_fondo='redondo'):
    """Una tecla dibujada: el fondo (circulo o pastilla) y el texto encima."""
    im = forma(forma_fondo, ancho, alto, fondo)
    im.alpha_composite(texto(txt, int(ancho * 0.72), int(alto * 0.72), letra),
                       (int(ancho * 0.14), int(alto * 0.14)))
    return im


def tecla_forma(tipo, ancho, alto, color, fondo=GRIS):
    """Una tecla con una forma dentro (la cruz, el circulo, el cuadrado o el triangulo de PlayStation)."""
    im = forma('redondo', ancho, alto, fondo)
    dentro = int(ancho * 0.60)
    im.alpha_composite(forma(tipo, dentro, dentro, color), ((ancho - dentro) // 2, (alto - dentro) // 2))
    return im


def dibujos():
    """{estilo: {boton: imagen}} con las formas y las letras de cada estilo."""
    ps = {
        'A': tecla_forma('cruz', 64, 64, AZUL),
        'B': tecla_forma('circulo', 64, 64, ROJO),
        'X': tecla_forma('cuadrado', 64, 64, ROSA),
        'Y': tecla_forma('triangulo', 64, 64, VERDE),
        'LB': tecla('L1', 64, 64), 'RB': tecla('R1', 64, 64),
        'LT': tecla('L2', 64, 64, forma_fondo='pastilla'), 'RT': tecla('R2', 64, 64, forma_fondo='pastilla'),
        'BACK': tecla('SEL', 64, 64, forma_fondo='pastilla'), 'START': tecla('STA', 64, 64, forma_fondo='pastilla'),
    }
    switch = {
        'A': tecla('A', 64, 64), 'B': tecla('B', 64, 64),
        'X': tecla('X', 64, 64), 'Y': tecla('Y', 64, 64),
        'LB': tecla('L', 64, 64), 'RB': tecla('R', 64, 64),
        'LT': tecla('ZL', 64, 64, forma_fondo='pastilla'), 'RT': tecla('ZR', 64, 64, forma_fondo='pastilla'),
        'BACK': tecla('-', 64, 64, forma_fondo='pastilla'), 'START': tecla('+', 64, 64, forma_fondo='pastilla'),
    }
    for style in (ps, switch):
        for key in ('A', 'B', 'X', 'Y'):
            original = style[key]
            grey = ImageOps.grayscale(original).convert('RGBA')
            grey.putalpha(original.getchannel('A'))
            style[key + 'GREY'] = grey
    for style in (ps, switch):
        style['LS'] = tecla('L3', 64, 64)
        style['RS'] = tecla('R3', 64, 64)
    return {'ps': ps, 'switch': switch}


def caja(im):
    """(x0, y0, x1, y1) de lo que no es transparente."""
    a = np.array(im)[:, :, 3]
    ys, xs = np.nonzero(a > 40)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1) if len(xs) else (0, 0, im.width, im.height)


def encajar(icono, w, h):
    """El icono del mayor tamano que entra en w x h sin deformarse, centrado en un lienzo w x h."""
    f = min(w / icono.width, h / icono.height)
    nuevo = icono.resize((max(1, round(icono.width * f)), max(1, round(icono.height * f))), Image.LANCZOS)
    lienzo = Image.new('RGBA', (max(1, w), max(1, h)), (0, 0, 0, 0))
    lienzo.alpha_composite(nuevo, (((w - nuevo.width) // 2), ((h - nuevo.height) // 2)))
    return lienzo


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--data', required=True, help='carpeta del juego preparada (Data_Core.wad, Update001.wad)')
    ap.add_argument('--out', required=True, help='carpeta donde dejar las variantes')
    a = ap.parse_args()
    core = os.path.join(a.data, 'Data_Core.wad')
    update = os.path.join(a.data, 'Update001.wad')
    if not os.path.exists(core):
        sys.exit('missing %s' % core)
    if not os.path.exists(update):
        sys.exit('missing %s' % update)

    estilos = dibujos()
    # 1. Las hojas de iconos y las texturas de los botones, sacadas por su nombre.
    queridos = {}
    for ruta, datos in wad12.recorre(core, lambda n: ('XBOX_' in n and n.endswith('.TDX'))
                                     or n.endswith('SYMBOLS.TDX') or n.endswith('SYMBOLS_FE.TDX')):
        queridos[ruta] = datos
    print('%d button textures in Data_Core.wad' % len(queridos))

    cambios = {}
    for estilo, dib in estilos.items():
        for ruta, datos in queridos.items():
            carpeta, nombre = ruta.rsplit('/', 1)
            if not (carpeta.endswith(TEX) or carpeta.endswith(TEX + '/BUTTONS') or carpeta.endswith(TEX360)):
                continue
            if not nombre.startswith('XBOX_') or not nombre.endswith('.TDX'):
                continue
            boton = nombre[5:-4]
            if boton not in dib:
                continue  # los brillos quedan como estan
            im, niveles, banderas, fmt = leer_tdx(datos)
            if im is None or im.size != (64, 64):
                continue  # las grises van comprimidas: se quedan como estan
            x0, y0, x1, y1 = caja(im)
            nuevo = Image.new('RGBA', im.size, (0, 0, 0, 0))
            nuevo.alpha_composite(encajar(dib[boton], x1 - x0, y1 - y0), (x0, y0))
            cambios['%s/%s' % (estilo, ruta)] = escribir_tdx(nuevo, banderas)

        # 2. La hoja de iconos de los textos: SYMBOLS y SYMBOLS_FE.
        for hoja_ruta in [r for r in queridos if r.endswith('SYMBOLS.TDX') or r.endswith('SYMBOLS_FE.TDX')]:
            original = queridos[hoja_ruta]
            im, niveles, banderas, fmt = leer_tdx(original)
            if im is None:
                continue
            for boton, (y0, x0, y1, x1) in CASILLAS.items():
                # Se limpia la casilla entera de 84 pixeles (incluye el texto de SELECT/START y los bordes del
                # boton de Xbox) y se pone el dibujo nuevo en la caja que ocupaba el viejo.
                cx, cy = (x0 // 84) * 84, (y0 // 84) * 84
                im.paste((0, 0, 0, 0), (cx, cy, min(cx + 84, im.width), min(cy + 84, im.height)))
                im.alpha_composite(encajar(dib[boton], x1 - x0, y1 - y0), (x0, y0))
            # Los 11 niveles originales y la cola empaquetada se conservan: el cargador de fuentes los espera.
            datos = bytearray(original)
            offset = 20 + struct.unpack_from('<I', datos, 16)[0]
            nivel = im
            while nivel.width >= 32:
                pixeles = nivel.tobytes('raw', 'BGRA')
                datos[offset:offset + len(pixeles)] = pixeles
                offset += len(pixeles)
                nivel = nivel.resize((nivel.width // 2, nivel.height // 2), Image.LANCZOS)
            cambios['%s/%s' % (estilo, hoja_ruta)] = bytes(datos)

    # 3. Los dos WAD de variante: Update001.wad con las texturas cambiadas.
    original, fecha = wad12.leer(update)
    hechos = 0
    for estilo in estilos:
        fs = dict(original)
        n = 0
        for clave, datos in cambios.items():
            if not clave.startswith(estilo + '/'):
                continue
            ruta = clave.split('/', 1)[1].split('DATA_CORE/')[-1]
            fs['UPDATE001/' + ruta] = datos
            n += 1
        salida = os.path.join(a.out, 'mtg12_buttons_%s.bin' % estilo)
        os.makedirs(a.out, exist_ok=True)
        wad12.escribir(fs, salida, fecha or 0x3F099984)
        print('%s: %d textures replaced; %d original WAD entries' % (salida, n, len(original)))
        hechos += 1
    print('done: %d variants in %s' % (hechos, a.out))


if __name__ == '__main__':
    main()
