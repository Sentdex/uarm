import cv2
import numpy as np

RESCALE_FACTOR = 0.5

cap = cv2.VideoCapture(0)
cap.set(3, int(1280*RESCALE_FACTOR))
cap.set(4, int(720*RESCALE_FACTOR))

while 1:
    _, frame = cap.read()
    frame = cv2.resize(frame, (300, 150))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0,  120, 120])
    upper_red = np.array([20, 255, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(frame,frame, mask= mask)

    kernel = np.ones((15,15),np.float32)/225
    smoothed = cv2.filter2D(res,-1,kernel)
    cv2.imshow('Original',frame)
    cv2.imshow('Averaging',smoothed)

    _, puck = cv2.threshold(smoothed, 30, 255, cv2.THRESH_BINARY)
    cv2.imshow('Puck',puck)

    print(puck)
    # x, y
    # y, x
    print(np.where(puck!=0)[0])
    print(np.where(puck!=0)[1])

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
