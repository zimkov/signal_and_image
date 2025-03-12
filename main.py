import sys
from PIL import Image
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtGui import QPixmap, QColor, QImage
from PyQt6.QtCore import Qt
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.img = None
        self.ui = Ui_Color_Convereter()  # Создаем экземпляр сгенерированного класса
        self.ui.setupUi(self)  # Настраиваем интерфейс
        self.mode_color = False
        self.path = None

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

        self.ui.slider_r.setRange(0, 255)
        self.ui.slider_r.valueChanged.connect(self.update_slider_r)
        self.ui.slider_g.setRange(0, 255)
        self.ui.slider_g.valueChanged.connect(self.update_slider_g)
        self.ui.slider_b.setRange(0, 255)
        self.ui.slider_b.valueChanged.connect(self.update_slider_b)

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
        self.ui.takeColorBtn.clicked.connect(self.take_color_mode)
        self.ui.image_label.mousePressEvent = self.take_color

    def take_color_mode(self):
        if self.mode_color:
            self.mode_color = False
        else:
            self.mode_color = True
        print(self.mode_color)

    def take_color(self, event):
        if self.mode_color:
            x = event.pos().x()
            y = event.pos().y()
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

                    # Отображаем информацию
                    self.ui.info_label.setText(info)
                except Exception as e:
                    self.ui.info_label.setText(f"Ошибка при отображении изображения: {e}")
            else:
                self.ui.info_label.setText(info)

    def update_slider_r(self, value):
        self.ui.rgb_r.setValue(value)
        self.update_colors(self.ui.slider_r.value(), self.ui.slider_g.value(), self.ui.slider_b.value())

    def update_slider_g(self, value):
        self.ui.rgb_g.setValue(value)
        self.update_colors(self.ui.slider_r.value(), self.ui.slider_g.value(), self.ui.slider_b.value())

    def update_slider_b(self, value):
        self.ui.rgb_b.setValue(value)
        self.update_colors(self.ui.slider_r.value(), self.ui.slider_g.value(), self.ui.slider_b.value())

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
