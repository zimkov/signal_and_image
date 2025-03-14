import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance


class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")

        self.image = None
        self.original_image = None

        # Создаем интерфейс
        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        self.brightness_slider = tk.Scale(root, from_=0, to=2, resolution=0.1, label="Brightness", orient=tk.HORIZONTAL,
                                          command=self.update_image)
        self.brightness_slider.set(1)  # Значение по умолчанию
        self.brightness_slider.pack()

        self.contrast_slider = tk.Scale(root, from_=0, to=2, resolution=0.1, label="Contrast", orient=tk.HORIZONTAL,
                                        command=self.update_image)
        self.contrast_slider.set(1)  # Значение по умолчанию
        self.contrast_slider.pack()

        self.saturation_slider = tk.Scale(root, from_=0, to=2, resolution=0.1, label="Saturation", orient=tk.HORIZONTAL,
                                          command=self.update_image)
        self.saturation_slider.set(1)  # Значение по умолчанию
        self.saturation_slider.pack()

        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_image = Image.open(file_path)
            self.image = self.original_image.copy()
            self.display_image()

    def display_image(self):
        if self.image:
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def update_image(self, event=None):
        if self.original_image:
            brightness = self.brightness_slider.get()
            contrast = self.contrast_slider.get()
            saturation = self.saturation_slider.get()

            # Применяем изменения
            img_enhancer = ImageEnhance.Brightness(self.original_image)
            self.image = img_enhancer.enhance(brightness)

            img_enhancer = ImageEnhance.Contrast(self.image)
            self.image = img_enhancer.enhance(contrast)

            img_enhancer = ImageEnhance.Color(self.image)
            self.image = img_enhancer.enhance(saturation)

            self.display_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
