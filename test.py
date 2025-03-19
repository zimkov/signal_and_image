import cv2
import numpy as np

cap = cv2.VideoCapture(0)  # Или путь к видеофайлу

backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Увеличение контрастности
    alpha = 1.5
    beta = 0
    frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

    fgMask = backSub.apply(frame)

    # Морфологические операции для очистки маски
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
    fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel)
    fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_CLOSE, kernel)

    # Применение маски к оригинальному кадру
    result = cv2.bitwise_and(frame, frame, mask=fgMask)

    # Отображение результатов
    cv2.imshow('Frame', frame)
    cv2.imshow('FG Mask', fgMask)
    cv2.imshow('Result', result)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
