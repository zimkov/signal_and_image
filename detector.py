import cv2
import numpy as np

from PyQt6.QtWidgets import QWidget, QPushButton, \
    QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog, QProgressDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimediaWidgets import QVideoWidget


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.setGeometry(200, 200, 700, 400)
        self.setWindowTitle("PyQt Media Player")
        self.setWindowIcon(QIcon('player.ico'))

        self.mediaplayer = QMediaPlayer()
        self.audio = QAudioOutput()

        videowidget = QVideoWidget()

        # btn for opening
        openBtn = QPushButton("Открыть видео")
        openBtn.clicked.connect(self.open_video)

        # btn for palying
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        # slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        hbox = QHBoxLayout()

        hbox.addWidget(openBtn)
        hbox.addWidget(self.playBtn)
        hbox.addWidget(self.slider)

        vbox = QVBoxLayout()

        vbox.addWidget(videowidget)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.mediaplayer.setVideoOutput(videowidget)
        self.mediaplayer.setAudioOutput(self.audio)

        # media player signals
        self.mediaplayer.mediaStatusChanged.connect(self.mediastate_changed)
        self.mediaplayer.positionChanged.connect(self.position_changed)
        self.mediaplayer.durationChanged.connect(self.duration_changed)

    def open_video(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.video_path = filename
            self.mediaplayer.setSource(QUrl.fromLocalFile(filename))
            self.playBtn.setEnabled(True)

    def open_video_path(self, path):
        self.mediaplayer.setSource(QUrl.fromLocalFile(path))
        self.playBtn.setEnabled(True)

    def play_video(self):
        if self.mediaplayer.mediaStatus == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaplayer.pause()

        else:
            self.mediaplayer.play()

    def mediastate_changed(self):
        if self.mediaplayer.mediaStatus == QMediaPlayer.PlaybackState.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )

        else:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaplayer.setPosition(position)

    def delete_back(self):
        file_path = self.video_path
        out_path = r'.\img\no_background.mp4'
        video = cv2.VideoCapture(file_path)

        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)

        out = cv2.VideoWriter(out_path, 14, fps, (frame_width, frame_height))

        backSub_mog = cv2.createBackgroundSubtractorKNN()
        nframe = 0
        progress_bar = QProgressDialog()
        progress_bar.create()
        progress_bar.setLabelText('Обработка видео...')
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))
        while True:
            ret, frame = video.read()

            progress_bar.setValue(nframe)
            nframe += 1
            if not ret:
                break

            if progress_bar.wasCanceled():
                break

            if ret:
                fg_mask = backSub_mog.apply(frame)

                # Find contours
                contours, hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Define minimum contour area
                min_contour_area = 200
                large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

                # Create a mask for the large contours
                mask = np.zeros_like(frame)  # Create a black mask
                cv2.drawContours(mask, large_contours, -1, (255, 255, 255),
                                 thickness=cv2.FILLED)  # Fill the mask with white for the contours

                # Bitwise AND to keep only the moving objects
                frame_out = cv2.bitwise_and(frame, mask)
                out.write(frame_out)
                # Show the final frame
                # cv2.imshow('Frame_final', frame_out)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                video = cv2.VideoCapture(file_path)

        cv2.destroyAllWindows()
        video.release()

        self.open_video_path(out_path)

    def motion_blur(self):
        file_path = self.video_path
        out_path = r'.\img\blur.mp4'
        video = cv2.VideoCapture(file_path)

        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)

        out = cv2.VideoWriter(out_path, 14, fps, (frame_width, frame_height))

        backSub_mog = cv2.createBackgroundSubtractorMOG2()
        nframe = 0
        progress_bar = QProgressDialog()
        progress_bar.create()
        progress_bar.setLabelText('Обработка видео...')
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))
        while True:
            # Read image
            ret, img = video.read()

            progress_bar.setValue(nframe)
            nframe += 1
            if not ret:
                break

            if progress_bar.wasCanceled():
                break

            if ret:
                fg_mask = backSub_mog.apply(img)

                contours, hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                min_contour_area = 5000
                large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

                mask = np.zeros_like(img, dtype=np.uint8)
                cv2.drawContours(mask, large_contours, -1, (255, 255, 255),
                                 thickness=cv2.FILLED)

                kernel_size = 15
                kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)

                for i in range(kernel_size):
                    kernel[i, :] = np.ones(kernel_size)

                kernel /= kernel_size * kernel_size

                blurred_img = cv2.filter2D(img, -1, kernel)

                inverted_mask = cv2.bitwise_not(mask)

                sharp_background = cv2.bitwise_and(img, inverted_mask)
                blurred_moving_objects = cv2.bitwise_and(blurred_img, mask)

                # Combine both images
                final_output = cv2.add(sharp_background, blurred_moving_objects)
                out.write(final_output)
                # Show the final frame
                # cv2.imshow('Frame_final', final_output)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                video = cv2.VideoCapture(file_path)

        # Close camera
        video.release()
        cv2.destroyAllWindows()

        self.open_video_path(out_path)


def detector_harris(image):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    new_image_bgr = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

    operatedImage = cv2.cvtColor(new_image_bgr, cv2.COLOR_BGR2GRAY)
    operatedImage = np.float32(operatedImage)

    dest = cv2.cornerHarris(operatedImage, 2, 5, 0.07)
    dest = cv2.dilate(dest, None)

    corners = dest > 0.01 * dest.max()
    new_image_bgr[corners] = [0, 0, 255]

    new_image_bgr = cv2.cvtColor(new_image_bgr, cv2.COLOR_BGR2RGBA)
    return new_image_bgr


def detector_sift(image):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT.create()
    kp = sift.detect(gray, None)

    # Marking the keypoint on the image using circles
    image = cv2.drawKeypoints(gray,
                            kp,
                            image,
                            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return image


def detector_surf(image):
    pass
    # if image is None:
    #     print("Ошибка: не удалось загрузить изображение.")
    #     return None
    #
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #
    # # Инициализация детектора SURF
    # surf = cv2.xfeatures2d.SURF.create(hessianThreshold=400)
    #
    # # Обнаружение ключевых точек и вычисление дескрипторов
    # keypoints, descriptors = surf.detectAndCompute(gray, None)
    #
    # # Рисуем ключевые точки на изображении
    # img_with_keypoints = cv2.drawKeypoints(gray, keypoints, None, (0, 255, 0),
    #                                        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    #
    # # Преобразование обратно в QImage
    # img_with_keypoints = cv2.cvtColor(img_with_keypoints, cv2.COLOR_BGR2RGBA)
    # return img_with_keypoints


def detector_fast(image):
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return None

    fast = cv2.FastFeatureDetector.create(threshold=25)

    kp = fast.detect(image, None)
    img2 = cv2.drawKeypoints(image, kp, None, color=(255, 0, 0))
    return img2


def find_sim(images: list):
    hist = []
    for img in images:
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        histogram = cv2.calcHist([gray_image], [0],
                              None, [256], [0, 256])
        hist.append(histogram)

    img1 = 0
    img2 = 1
    c = 1000000
    c1 = 0
    for i in range(len(hist)):
        for j in range(i + 1, len(hist)):
            h = 0
            c1 = 0
            while h < len(hist[i]) and h < len(hist[j]):
                c1 += (hist[i][h] - hist[j][h]) ** 2
                h += 1
            c1 = c1 ** (1 / 2)
            if c1 < c:
                img1 = i
                img2 = j
                c = c1
            print(f'c = {c}, c1 = {c1}, [{i}, {j}]')
    return img1, img2


if __name__ == '__main__':
    image = cv2.imread(r'C:\Users\Admin\Desktop\Alexei\pythonProjects\testPyQT\signal_and_image\img\2.jpg')
    new_image = detector_fast(image)
    cv2.imshow('Image with Borders', new_image)

    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()