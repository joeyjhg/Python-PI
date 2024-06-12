import cv2
import numpy as np


def Coin_Detection(frame):

    coin_detection = False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        1.15,
        80,
        param1=70,
        param2=85,
        minRadius=10,
        maxRadius=60,
    )

    if circles is not None:
        coin_detection = True
        for i in circles[0, :]:
            center = (i[0], i[1])  # 원의 중심 좌표
            radius = i[2]  # 원의 반지름
            x, y = center - radius
            x = int(x)
            y = int(y)

            if x < 0 or y < 0:
                continue

            cv2.circle(
                frame,
                (int(i[0]), int(i[1])),
                int(radius),
                (0, 255, 0),
                3,
                cv2.LINE_AA,
                0,
            )

            roi = frame[y : y + int(radius) * 2, x : x + int(radius) * 2]

            img_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            middle_row = img_hsv[img_hsv.shape[0] // 2]

            middle_pixel_index = img_hsv.shape[1] // 2

            h = middle_row[middle_pixel_index, 0]  # H channel
            s = middle_row[middle_pixel_index, 1]  # S channel
            v = middle_row[middle_pixel_index, 2]  # V channel

    return coin_detection  # 동전 검출 여부 반환


def Coin_Detection_save(frame, money_process_filename):

    coin_detection = False
    frame_copy = frame.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        1.15,
        80,
        param1=70,
        param2=85,
        minRadius=10,
        maxRadius=60,
    )

    if circles is not None:
        coin_detection = True

        for i in circles[0, :]:
            center = (i[0], i[1])  # 원의 중심 좌표
            radius = i[2]  # 원의 반지름
            x, y = center - radius
            x = int(x)
            y = int(y)

            if x < 0 or y < 0:
                continue

            cv2.circle(
                frame,
                (int(i[0]), int(i[1])),
                int(radius),
                (0, 255, 0),
                3,
                cv2.LINE_AA,
                0,
            )
            roi = frame[y : y + int(radius) * 2, x : x + int(radius) * 2]

            img_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            middle_row = img_hsv[img_hsv.shape[0] // 2]

            middle_pixel_index = img_hsv.shape[1] // 2

            h = middle_row[middle_pixel_index, 0]  # H channel
            s = middle_row[middle_pixel_index, 1]  # S channel
            v = middle_row[middle_pixel_index, 2]  # V channel

        cv2.imwrite(money_process_filename, frame)
    else:
        cv2.imwrite(money_process_filename, frame_copy)

    return coin_detection  # 동전 검출 여부 반환
