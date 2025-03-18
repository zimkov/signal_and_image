import cv2
import numpy as np


def erosion(image, kernel_size=(5, 5), iterations=1):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    kernel = np.ones(kernel_size, np.uint8)
    eroded_image = cv2.erode(image, kernel, iterations=iterations)
    return eroded_image


def dilation(image, kernel_size=(5, 5), iterations=1):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    kernel = np.ones(kernel_size, np.uint8)
    dilated_image = cv2.dilate(image, kernel, iterations=iterations)
    return dilated_image


def opening(image, kernel_size=(5, 5), iterations=1):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    kernel = np.ones(kernel_size, np.uint8)
    opened_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
    return opened_image


def closing(image, kernel_size=(5, 5), iterations=1):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    kernel = np.ones(kernel_size, np.uint8)
    closed_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    return closed_image


def gradient(image, kernel_size=(5, 5)):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    kernel = np.ones(kernel_size, np.uint8)
    gradient_image = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)
    return gradient_image