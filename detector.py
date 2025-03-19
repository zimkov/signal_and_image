import cv2
import numpy as np


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