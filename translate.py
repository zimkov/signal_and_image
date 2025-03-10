import numpy as np


def rgb_to_cmyk(r: int, g: int, b: int) -> list:
    r = r / 255
    g = g / 255
    b = b / 255

    k = 1 - np.maximum(np.maximum(r, g), b)

    c = (1 - r - k) / (1 - k + 1e-10)
    m = (1 - g - k) / (1 - k + 1e-10)
    y = (1 - b - k) / (1 - k + 1e-10)

    return [round(c * 100), round(m * 100), round(y * 100), round(k * 100)]


def cmyk_to_rgb(c: float, m: float, y: float, k: float):

    c = c
    m = m
    y = y
    k = k

    r = (1 - c) * (1 - k)
    g = (1 - m) * (1 - k)
    b = (1 - y) * (1 - k)

    return [r, g, b]


def rgb_to_hsl(r: int, g: int, b: int):
    r /= 255.0
    g /= 255.0
    b /= 255.0

    max_val = max(r, g, b)
    min_val = min(r, g, b)

    l = (max_val + min_val) / 2

    if max_val == min_val:
        s = 0
        h = 0
    else:
        if l < 0.5:
            s = (max_val - min_val) / (max_val + min_val)
        else:
            s = (max_val - min_val) / (2 - max_val - min_val)

        if max_val == r:
            h = (g - b) / (max_val - min_val)
        elif max_val == g:
            h = 2 + (b - r) / (max_val - min_val)
        else:  # max_val == b
            h = 4 + (r - g) / (max_val - min_val)

        h *= 60
        if h < 0:
            h += 360

    s *= 100
    l *= 100

    return [round(h), round(s), round(l)]


def hsl_to_rgb(h: float, s: float, l: float):
    h = h / 360
    s = s / 100
    l = l / 100

    if s == 0:
        r = g = b = l  # Achromatic (grey)
    else:
        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q

        r = hue_to_rgb(p, q, h + 1 / 3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1 / 3)

    return [r * 255, g * 255, b * 255]


def rgb_to_hsv(r: int, g: int, b: int):

    r /= 255.0
    g /= 255.0
    b /= 255.0

    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn

    if df == 0:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    elif mx == b:
        h = (60 * ((r - g) / df) + 240) % 360

    s = 0 if mx == 0 else (df / mx)

    v = mx

    return [round(h), round(s * 100), round(v * 100)]


def hsv_to_rgb(h: int, s: int, v: int):
    s /= 100.0
    v /= 100.0

    if s == 0:  # Если насыщенность равна 0, цвет будет серым
        r = g = b = int(v * 255)
        return [r, g, b]

    i = int(h // 60)  # Определяем сектор
    f = (h / 60) - i  # Остаток от деления
    p = v * (1 - s)  # Значение p
    q = v * (1 - f * s)  # Значение q
    t = v * (1 - (1 - f) * s)  # Значение t

    # В зависимости от сектора определяем значения RGB
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    elif i == 5:
        r, g, b = v, p, q

    return [int(r * 255), int(g * 255), int(b * 255)]


def rgb_to_xyz(r, g, b):
    r /= 255.0
    g /= 255.0
    b /= 255.0

    # Применяем обратное гамма-корректирование
    r = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4

    # Преобразуем в XYZ
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    x *= 100
    y *= 100
    z *= 100

    return [x, y, z]


def xyz_to_lab(x, y, z):
    x /= 95.047
    y /= 100.000
    z /= 108.883

    # Применяем обратное преобразование
    x = x ** (1/3) if x > 0.008856 else (x * 7.787 + 16 / 116)
    y = y ** (1/3) if y > 0.008856 else (y * 7.787 + 16 / 116)
    z = z ** (1/3) if z > 0.008856 else (z * 7.787 + 16 / 116)

    l = max(0, (116 * y) - 16)
    a = (x - y) * 500
    b = (y - z) * 200

    return [round(l), round(a), round(b)]


def lab_to_xyz(l, a, b):
    # Обратное преобразование LAB в XYZ
    y = (l + 16) / 116
    x = a / 500 + y
    z = y - b / 200

    # Обратное нормирование по D65
    x = 95.047 * (x ** 3 if x ** 3 > 0.008856 else (x - 16 / 116) / 7.787)
    y = 100.000 * (y ** 3 if y ** 3 > 0.008856 else (y - 16 / 116) / 7.787)
    z = 108.883 * (z ** 3 if z ** 3 > 0.008856 else (z - 16 / 116) / 7.787)

    return [x, y, z]


def xyz_to_rgb(x, y, z):
    # Преобразуем XYZ в RGB
    x /= 100.0
    y /= 100.0
    z /= 100.0

    r = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
    g = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
    b = x * 0.0556434 + y * -0.2040259 + z * 1.0572252

    # Применяем гамма-корректировку
    r = 12.92 * r if r <= 0.0031308 else (1.055 * (r ** (1/2.4)) - 0.055)
    g = 12.92 * g if g <= 0.0031308 else (1.055 * (g ** (1/2.4)) - 0.055)
    b = 12.92 * b if b <= 0.0031308 else (1.055 * (b ** (1/2.4)) - 0.055)

    # Нормализуем значения от 0 до 255
    r = max(0, min(255, round(r * 255)))
    g = max(0, min(255, round(g * 255)))
    b = max(0, min(255, round(b * 255)))

    return [r, g, b]


def lab_to_rgb(l, a, b):
    x, y, z = lab_to_xyz(l, a, b)
    return xyz_to_rgb(x, y, z)


def rgb_to_lab(r, g, b):
    x, y, z = rgb_to_xyz(r, g, b)
    return xyz_to_lab(x, y, z)


def rgb_to_ycbcr(r: int, g: int, b: int):
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    y  = 0.299 * r + 0.587 * g + 0.114 * b
    cb = 128 - 0.168736 * r - 0.331364 * g + 0.5 * b
    cr = 128 + 0.5 * r - 0.5 * g - 0.081312 * b

    return [round(int(y)), round(int(cb)), round(int(cr))]


def ycbcr_to_rgb(y, cb, cr):
    y = max(0, min(255, y))
    cb = max(0, min(255, cb))
    cr = max(0, min(255, cr))

    r = y + 1.402 * (cr - 128)
    g = y - 0.344136 * (cb - 128) - 0.714136 * (cr - 128)
    b = y + 1.772 * (cb - 128)

    r = int(max(0, min(255, r)))
    g = int(max(0, min(255, g)))
    b = int(max(0, min(255, b)))

    return [r, g, b]


if __name__ == "__main__":
    # Пример использования
    r, g, b = 200, 0, 0

    print(rgb_to_hsl(r, g, b))