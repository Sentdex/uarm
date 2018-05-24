import cv2
import numpy as np

RESCALE_FACTOR = 0.5

cap = cv2.VideoCapture(1)
cap.set(3, int(1280*RESCALE_FACTOR))
cap.set(4, int(720*RESCALE_FACTOR))

for i in range(15):
    _, frame = cap.read()

r = cv2.selectROI(frame)

while 1:
    _, frame = cap.read()

    img_crop = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

    hsv = cv2.cvtColor(img_crop, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 50, 0])
    upper_red = np.array([20, 255, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(img_crop, img_crop, mask=mask)
    blur = cv2.GaussianBlur(res, (15, 15), 0)
    cv2.imshow('Gaussian Blurring', blur)

    _, puck = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY)
    cv2.imshow('Puck', puck)

    xs = np.where(puck != 0)[1]
    ys = np.where(puck != 0)[0]

    xstd = np.std(xs)
    ystd = np.std(ys)

    x_init_avg = np.mean(xs)
    y_init_avg = np.mean(ys)

    xs = [x for x in xs if x <= x_init_avg+xstd or x >= x_init_avg-xstd]
    ys = [y for y in ys if y <= y_init_avg+xstd or y >= y_init_avg-xstd]
    xavg = np.mean(xs)
    yavg = np.mean(ys)

    print(xavg, yavg)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
