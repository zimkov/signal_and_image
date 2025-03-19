import cv2
import numpy as np


def sharpening(image):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened_image = cv2.filter2D(image, -1, kernel)
    return sharpened_image


def motion_blur(image):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    kernel_size = 30

    kernel_v = np.zeros((kernel_size, kernel_size))
    kernel_h = np.copy(kernel_v)

    kernel_v[:, int((kernel_size - 1) / 2)] = np.ones(kernel_size)
    kernel_h[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)

    kernel_v /= kernel_size
    kernel_h /= kernel_size

    vertical_mb = cv2.filter2D(image, -1, kernel_v)
    horizonal_mb = cv2.filter2D(image, -1, kernel_h)
    return vertical_mb


def emboss(image):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    emboss_kernel = np.array([[-1, 0, 0],
                              [0, 0, 0],
                              [0, 0, 1]])

    emboss_img = cv2.filter2D(src=image, ddepth=-1, kernel=emboss_kernel)
    return emboss_img


def median_blur(image):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    filtered_image = cv2.medianBlur(image, 11)
    return filtered_image


def detector_canny(image):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    t_lower = 50  # Lower Threshold
    t_upper = 150  # Upper threshold

    edge = cv2.Canny(image, t_lower, t_upper)
    return edge


def operator_roberts(image):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    kernel_x = np.array([[1, 0], [0, -1]], dtype=np.float32)
    kernel_y = np.array([[0, 1], [-1, 0]], dtype=np.float32)

    # Применяем операторы к изображению
    grad_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
    grad_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)

    # Вычисляем градиент
    gradient_magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)

    # Нормализуем результат до диапазона [0, 255]
    gradient_magnitude = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX)

    # Преобразуем в 8-битное изображение
    edge_image = np.uint8(gradient_magnitude)

    return edge_image

