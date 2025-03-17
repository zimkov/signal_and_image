import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.figure.set_facecolor(color=(0.2, 0.2, 0.2))

    def plot(self, img):
        cv_image = img

        if type(img) is QImage:
            cv_image = qimage_to_cv2(img)

        if type(img) is Image.Image:
            pil_image = img

            cv_image = np.array(pil_image)

            if cv_image.ndim == 3:  # Проверяем, что изображение цветное
                if cv_image.shape[2] == 4:  # Если изображение в формате RGBA
                    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGBA2BGR)
                else:  # Если изображение в формате RGB
                    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)

        image = cv_image

        self.figure.clear()

        ax = self.figure.add_subplot(111)
        for i, col in enumerate(['b', 'g', 'r']):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            ax.plot(hist, color=col)

            # print(1)

        self.canvas.draw()

    def plot_1channel(self, img, channel: str):
        cv_image = img

        if type(img) is QImage:
            cv_image = qimage_to_cv2(img)

        if type(img) is Image.Image:
            pil_image = img

            cv_image = np.array(pil_image)

            if cv_image.ndim == 3:  # Проверяем, что изображение цветное
                if cv_image.shape[2] == 4:  # Если изображение в формате RGBA
                    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGBA2BGR)
                else:  # Если изображение в формате RGB
                    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)

        image = cv_image
        i = 0
        if channel == 'b':
            i = 0
        if channel == 'g':
            i = 1
        if channel == 'r':
            i = 2

        self.figure.clear()

        ax = self.figure.add_subplot(111)
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        ax.plot(hist, color=channel)

        self.canvas.draw()


def gray_img(img):
    img = cv2.imread(img)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('grayscale_image_opencv.jpg', gray_img)
    return gray_img


def qimage_to_cv2(qimage: QImage):
    """Преобразование QImage в формат, который может быть использован в OpenCV."""
    # Получаем данные изображения
    width = qimage.width()
    height = qimage.height()
    ptr = qimage.bits()
    ptr.setsize(qimage.sizeInBytes())  # Устанавливаем размер данных

    # Создаем массив NumPy из данных QImage
    img = np.array(ptr).reshape(height, width, 4)  # 4 канала (RGBA)

    # Преобразуем из RGBA в BGR (формат, используемый OpenCV)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    return img


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


if __name__ == "__main__":
    pass
