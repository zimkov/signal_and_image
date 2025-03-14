import cv2


def gray_img(img):
    img = cv2.imread(img)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('grayscale_image_opencv.jpg', gray_img)
    return gray_img


if __name__ == "__main__":
    gray_img(r'img\2.jpg')
