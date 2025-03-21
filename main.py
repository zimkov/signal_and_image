import sys

from PIL import Image, ImageEnhance
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtGui import QPixmap, QColor, QImage
from PyQt6.QtCore import Qt

from detector import *
from filter import *
from img_convert import *
from morph import *
from translate import *
from interface import Ui_Color_Convereter
import os


def get_image_info(file_path):
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            color_depth = img.mode
            file_format = img.format
            file_size = os.path.getsize(file_path)

            info = (f"Файл: {file_path}\n"
                    f"Размер на диске: {file_size} байт\n"
                    f"Разрешение: {width}x{height}\n"
                    f"Глубина цвета: {color_depth}\n"
                    f"Формат файла: {file_format}")

            return img, info
    except Exception as e:
        return None, f"Ошибка при обработке файла {file_path}: {e}"


def display_image(image):
    # Преобразуем BGR в RGB для отображения в QLabel
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, channel = image_rgb.shape
    bytes_per_line = 3 * width
    q_image = QPixmap.fromImage(QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888))
    return q_image


def pil_image_to_qimage(pil_image: Image):
    """Преобразует PIL Image в QImage."""
    # Преобразуем PIL изображение в формат RGB
    rgb_image = pil_image.convert("RGB")
    # Получаем данные изображения
    width, height = rgb_image.size
    data = rgb_image.tobytes("raw", "RGB")

    # Создаем QImage из данных
    qimage = QImage(data, width, height, QImage.Format.Format_RGB888)
    return qimage


def qimage_to_pil_image(qimage: QImage):
    """Преобразует QImage в PIL Image."""
    # Получаем ширину и высоту изображения
    width = qimage.width()
    height = qimage.height()

    # Создаем пустой PIL Image
    pil_image = Image.new("RGB", (width, height))

    # Копируем данные из QImage в PIL Image
    qimage_data = qimage.bits()
    qimage_data.setsize(qimage.bytesPerLine() * height)

    # Заполняем PIL Image данными из QImage
    pil_image.frombytes(qimage_data.asstring(), "raw", "RGB", 0, 1)

    return pil_image


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.img_new = None
        self.img = None
        self.ui = Ui_Color_Convereter()  # Создаем экземпляр сгенерированного класса
        self.ui.setupUi(self)  # Настраиваем интерфейс
        self.mode_color = False
        self.path = None
        self.arrayImg = []
        self.arrayImgLabel = [
            self.ui.image_1, self.ui.image_2, self.ui.image_3, self.ui.image_4, self.ui.image_5,
            self.ui.image_6, self.ui.image_7, self.ui.image_8, self.ui.image_9, self.ui.image_10
        ]
        self.numImg = 0

        self.ui.pushButton.clicked.connect(self.open_file_dialog)

        items_property_100 = [
            self.ui.cmyk_c, self.ui.cmyk_m, self.ui.cmyk_y, self.ui.cmyk_k,
            self.ui.hsl_h, self.ui.hsl_s, self.ui.hsl_l,
            self.ui.hsv_h, self.ui.hsv_s, self.ui.hsv_v,
            self.ui.lab_l, self.ui.lab_a, self.ui.lab_b
        ]
        items_property_255 = [
            self.ui.rgb_r, self.ui.rgb_g, self.ui.rgb_b,
            self.ui.ycc_y, self.ui.ycc_cb, self.ui.ycc_cr
        ]

        self.ui.brightness_slider.setRange(0, 20)
        self.ui.brightness_slider.setValue(10)
        self.ui.brightness_slider.setSingleStep(1)
        self.ui.brightness_slider.valueChanged.connect(self.update_filter_image)
        self.ui.contrast_slider.setRange(0, 20)
        self.ui.contrast_slider.setValue(10)
        self.ui.contrast_slider.setSingleStep(1)
        self.ui.contrast_slider.valueChanged.connect(self.update_filter_image)
        self.ui.saturation_slider.setRange(0, 20)
        self.ui.saturation_slider.setValue(10)
        self.ui.saturation_slider.setSingleStep(1)
        self.ui.saturation_slider.valueChanged.connect(self.update_filter_image)

        for item in items_property_100:
            item.setRange(0, 100)
            item.lineEdit().setReadOnly(True)
            item.setStyleSheet("""
                                     QSpinBox::up-button, QSpinBox::down-button {
                                     width: 0;
                                     height: 0;
                                     }
                                    """)

        for item in items_property_255:
            item.setRange(0, 255)
            item.lineEdit().setReadOnly(True)
            item.setStyleSheet("""
                                     QSpinBox::up-button, QSpinBox::down-button {
                                     width: 0;
                                     height: 0;
                                     }
                                    """)
        self.ui.takeColorBtn.setCheckable(True)
        self.ui.takeColorBtn.clicked.connect(self.take_color_mode)
        self.ui.image_label.mousePressEvent = self.take_color

        self.ui.funGrayBtn.setEnabled(False)
        self.ui.funGrayBtn.clicked.connect(self.get_gray_image)

        if not self.ui.gistoWidget.layout():
            self.ui.gistoWidget.setLayout(QVBoxLayout())
        self.plot_widget = PlotWidget()
        self.ui.gistoWidget.layout().addWidget(self.plot_widget)

        if not self.ui.widget.layout():
            self.ui.widget.setLayout(QVBoxLayout())
        self.video_widget = VideoPlayer()
        self.ui.widget.layout().addWidget(self.video_widget)

        self.ui.allChannelBtn.clicked.connect(self.update_gisto_image)
        self.ui.rChannelBtn.clicked.connect(self.update_gisto_rchannel)
        self.ui.gChannelBtn.clicked.connect(self.update_gisto_gchannel)
        self.ui.bChannelBtn.clicked.connect(self.update_gisto_bchannel)

        self.ui.linearBtn.clicked.connect(self.update_linear)
        self.ui.unlinearBtn.clicked.connect(self.update_unlinear)

        self.ui.erosBtn.clicked.connect(self.update_erosian)
        self.ui.dilBtn.clicked.connect(self.update_dilation)
        self.ui.openmorphBtn.clicked.connect(self.update_opening)
        self.ui.closemorphBtn.clicked.connect(self.update_closing)
        self.ui.gradBtn.clicked.connect(self.update_gradient)

        self.ui.filter1Btn.clicked.connect(self.update_sharpening)
        self.ui.filter2Btn.clicked.connect(self.update_motion_blur)
        self.ui.filter3Btn.clicked.connect(self.update_emboss)
        self.ui.filter4Btn.clicked.connect(self.update_median_blur)
        self.ui.filter5Btn.clicked.connect(self.update_detector_canny)
        self.ui.filter6Btn.clicked.connect(self.update_operator_roberts)

        self.ui.detector1Btn.clicked.connect(self.update_detector_harris)
        self.ui.detector2Btn.clicked.connect(self.update_detector_sift)
        self.ui.detector3Btn.clicked.connect(self.update_detector_surf)
        self.ui.detector4Btn.clicked.connect(self.update_detector_fast)

        self.ui.chooseImagesBtn.clicked.connect(self.add_img)
        self.ui.twice_image.clicked.connect(self.update_sim_img)
        self.ui.deleteBackground.clicked.connect(self.delete_background)
        self.ui.motionBlur.clicked.connect(self.motion_blur_video)

    def take_color_mode(self):
        if self.mode_color:
            self.mode_color = False
        else:
            if type(self.img) is Image:
                self.img = pil_image_to_qimage(self.img)
            self.mode_color = True
        print(self.mode_color)

    def take_color(self, event):
        if self.mode_color:
            x = event.pos().x()
            y = event.pos().y()
            if type(self.img) is not QImage:
                self.img = pil_image_to_qimage(self.img)
            c = self.img.pixel(x, y)
            c_rgb = QColor(c).getRgb()  # 8bit RGBA: (255, 23, 0, 255)
            self.ui.color_view.setStyleSheet(
                f"background-color: rgb({c_rgb[0]}, {c_rgb[1]}, "
                f"{c_rgb[2]});\n"
                "border-radius: 15px;"
            )
            self.update_colors(c_rgb[0], c_rgb[1], c_rgb[2])

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp *.gif)")

        if file_path:
            img, info = get_image_info(file_path)
            self.path = file_path
            if img:
                # Отображаем изображение
                try:
                    self.img = QImage(file_path)
                    # img_qt = QPixmap(file_path).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
                    img_qt = QPixmap(QPixmap.fromImage(self.img))
                    self.ui.image_label.setPixmap(img_qt)
                    self.ui.image_label.setFixedWidth(img.size[0])
                    self.ui.image_label.setFixedHeight(img.size[1])
                    self.ui.takeColorBtn.setEnabled(True)
                    self.ui.funGrayBtn.setEnabled(True)
                    # Отображаем информацию
                    self.ui.info_label.setText(info)
                    self.update_gisto_image()
                except Exception as e:
                    self.ui.info_label.setText(f"Ошибка при отображении изображения: {e}")
            else:
                self.ui.info_label.setText(info)

    def add_img(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp *.gif)")

        if file_path:
            img, info = get_image_info(file_path)
            if img:
                # Отображаем изображение
                try:
                    self.arrayImg.append(QImage(file_path))
                    img_qt = (QPixmap(QPixmap.fromImage(self.arrayImg[self.numImg]))
                              .scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                    self.arrayImgLabel[self.numImg].setPixmap(img_qt)
                    if self.numImg < 9:
                        self.numImg += 1
                    else:
                        self.ui.chooseImagesBtn.setEnabled(False)
                except Exception as e:
                    self.ui.info_label.setText(f"Ошибка при отображении изображения: {e}")
            else:
                self.ui.info_label.setText(info)

    def update_sim_img(self):
        for i in range(len(self.arrayImg)):
            self.arrayImg[i] = qimage_to_cv2(self.arrayImg[i])

        img1, img2 = find_sim(self.arrayImg)
        img_qt1 = display_image(self.arrayImg[img1]).scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.image_result1.setPixmap(img_qt1)
        img_qt2 = display_image(self.arrayImg[img2]).scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.image_result2.setPixmap(img_qt2)

    def update_filter_image(self):
        if self.img:
            brightness = self.ui.brightness_slider.value() / 10
            contrast = self.ui.contrast_slider.value() / 10
            saturation = self.ui.saturation_slider.value() / 10

            if type(self.img) is QImage:
                self.img = qimage_to_pil_image(self.img)

            # Применяем изменения
            img_enhancer = ImageEnhance.Brightness(Image.open(self.path))
            self.img = img_enhancer.enhance(brightness)

            img_enhancer = ImageEnhance.Contrast(self.img)
            self.img = img_enhancer.enhance(contrast)

            img_enhancer = ImageEnhance.Color(self.img)
            self.img = img_enhancer.enhance(saturation)

            img_qt = QPixmap(QPixmap.fromImage(pil_image_to_qimage(self.img)))
            self.ui.image_label.setPixmap(img_qt)
            self.update_gisto_image()
            # self.img = QImage(pil_image_to_qimage(self.img))

    def get_gray_image(self):
        if self.path and self.img is not None:
            img_qt = display_image(gray_img(self.path))
            self.ui.image_label.setPixmap(img_qt)
            self.img = QImage(img_qt)
            self.update_gisto_image()

    def update_gisto_image(self):
        if self.path and self.img is not None:
            self.plot_widget.plot(img=self.img)

    def update_gisto_rchannel(self):
        if self.path and self.img is not None:
            self.plot_widget.plot_1channel(img=self.img, channel='r')

    def update_gisto_gchannel(self):
        if self.path and self.img is not None:
            self.plot_widget.plot_1channel(img=self.img, channel='g')

    def update_gisto_bchannel(self):
        if self.path and self.img is not None:
            self.plot_widget.plot_1channel(img=self.img, channel='b')

    def img_to_cvimg(self):
        cv_image = self.img
        if type(self.img) is QImage:
            qimage = self.img

            width = qimage.width()
            height = qimage.height()
            ptr = qimage.bits()
            ptr.setsize(qimage.sizeInBytes())

            cv_image = np.array(ptr).reshape(height, width, 4)

            cv_image = cv2.cvtColor(cv_image, cv2.IMREAD_GRAYSCALE)

        if type(self.img) is Image.Image:
            pil_image = self.img

            cv_image = np.array(pil_image)

            if cv_image.ndim == 3:
                if cv_image.shape[2] == 4:
                    cv_image = cv2.cvtColor(cv_image, cv2.IMREAD_GRAYSCALE)
                else:
                    cv_image = cv2.cvtColor(cv_image, cv2.IMREAD_GRAYSCALE)
        return cv_image

    def update_linear(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(linear_correction(cv_image, alpha=1.5, beta=30))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_unlinear(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(gamma_correction(cv_image, gamma=2.2))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_erosian(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(erosion(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_dilation(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(dilation(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_opening(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(opening(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_closing(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(closing(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_gradient(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(gradient(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_sharpening(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(sharpening(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_motion_blur(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(motion_blur(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_emboss(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(emboss(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_median_blur(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(median_blur(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_detector_canny(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(detector_canny(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_operator_roberts(self):
        cv_image = self.img_to_cvimg()

        img_qt = display_image(operator_roberts(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_detector_harris(self):
        cv_image = self.img_to_cvimg()
        img_qt = display_image(detector_harris(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_detector_sift(self):
        cv_image = self.img_to_cvimg()
        img_qt = display_image(detector_sift(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_detector_surf(self):
        cv_image = self.img_to_cvimg()
        img_qt = display_image(detector_surf(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_detector_fast(self):
        cv_image = self.img_to_cvimg()
        img_qt = display_image(detector_fast(cv_image))
        self.ui.image_label.setPixmap(img_qt)
        self.img = QImage(img_qt)

    def update_colors(self, r, g, b):
        self.ui.color_view.setStyleSheet(
            f"background-color: rgb({r}, {g}, "
            f"{b});\n"
            "border-radius: 15px;")
        self.ui.rgb_r.setValue(r)
        self.ui.rgb_g.setValue(g)
        self.ui.rgb_b.setValue(b)

        cmyk = rgb_to_cmyk(r, g, b)
        self.ui.cmyk_c.setValue(cmyk[0])
        self.ui.cmyk_m.setValue(cmyk[1])
        self.ui.cmyk_y.setValue(cmyk[2])
        self.ui.cmyk_k.setValue(cmyk[3])

        hsl = rgb_to_hsl(r, g, b)
        self.ui.hsl_h.setValue(hsl[0])
        self.ui.hsl_s.setValue(hsl[1])
        self.ui.hsl_l.setValue(hsl[2])

        hsv = rgb_to_hsv(r, g, b)
        self.ui.hsv_h.setValue(hsv[0])
        self.ui.hsv_s.setValue(hsv[1])
        self.ui.hsv_v.setValue(hsv[2])

        lab = rgb_to_lab(r, g, b)
        self.ui.lab_l.setValue(lab[0])
        self.ui.lab_a.setValue(lab[1])
        self.ui.lab_b.setValue(lab[2])

        ycc = rgb_to_ycbcr(r, g, b)
        self.ui.ycc_y.setValue(ycc[0])
        self.ui.ycc_cb.setValue(ycc[1])
        self.ui.ycc_cr.setValue(ycc[2])

    def delete_background(self):
        self.video_widget.delete_back()

    def motion_blur_video(self):
        self.video_widget.motion_blur()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
