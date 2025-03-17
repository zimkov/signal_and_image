import cv2
import numpy as np


def linear_correction(image, alpha=1.0, beta=0):
    """
    Применяет линейную коррекцию к черно-белому изображению.

    :param image: Входное черно-белое изображение.
    :param alpha: Коэффициент контраста (по умолчанию 1.0).
    :param beta: Смещение яркости (по умолчанию 0).
    :return: Изображение после линейной коррекции.
    """
    corrected_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return corrected_image


def gamma_correction(image, gamma=1.0):
    """
    Применяет гамма-коррекцию к черно-белому изображению.

    :param image: Входное черно-белое изображение.
    :param gamma: Значение гаммы (по умолчанию 1.0).
    :return: Изображение после гамма-коррекции.
    """
    # Создаем массив для хранения результата
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")

    # Применяем таблицу преобразования
    corrected_image = cv2.LUT(image, table)
    return corrected_image


image = cv2.imread(r'C:\Users\Admin\Desktop\Alexei\pythonProjects\testPyQT\signal_and_image\img\2.jpg', cv2.IMREAD_GRAYSCALE)

# Применение линейной коррекции
linear_corrected = linear_correction(image, alpha=1.5, beta=30)

# Применение гамма-коррекции
gamma_corrected = gamma_correction(image, gamma=2.2)

# Отображение результатов
cv2.imshow('Original Image', image)
cv2.imshow('Linear Corrected Image', linear_corrected)
cv2.imshow('Gamma Corrected Image', gamma_corrected)
cv2.waitKey(0)
cv2.destroyAllWindows()

