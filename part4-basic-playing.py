import cv2
import numpy as np
from uf.wrapper.swift_api import SwiftAPI
import time
# what's the maximum in positive that the arm can do?
ARM_Y_MAX = 220
RESCALE_FACTOR = 0.5

cap = cv2.VideoCapture(1)
cap.set(3, int(1280*RESCALE_FACTOR))
cap.set(4, int(720*RESCALE_FACTOR))

# could not open port 'COM4': PermissionError(13, 'Access is denied.', None, 5)
accessed = False
while not accessed:
    try:
        swift = SwiftAPI()
        accessed = True
    except Exception as e:
        time.sleep(0.2)

print('device info: ')
print(swift.get_device_info())
swift.set_position(x=200, y=0, z=31, relative=False, speed=20000, wait=True)
swift.set_pump(True)


for i in range(15):
    _, frame = cap.read()

r = cv2.selectROI(frame)


# so it doesnt keep swinging to hit puck:
since_swing = 9999
while 1:
    _, frame = cap.read()

    img_crop = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

    hsv = cv2.cvtColor(img_crop, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 50, 0])
    upper_red = np.array([20, 255, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(img_crop, img_crop, mask = mask)
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

    # possibly if std is too high, we can consider that we have a problem?

    xs = [x for x in xs if x <= x_init_avg+xstd or x >= x_init_avg-xstd]
    ys = [y for y in ys if y <= y_init_avg+xstd or y >= y_init_avg-xstd]
    xavg = np.mean(xs)
    yavg = np.mean(ys)

    cropped_height, cropped_width, channels = img_crop.shape

    puck_x = xavg/cropped_width*100
    puck_y = yavg/cropped_height*100
    print("Puck X: {}%    Puck Y: {}%".format(puck_x, puck_y))

    desired_arm_y = ((puck_y/100.0)*(ARM_Y_MAX*2))-ARM_Y_MAX

    print('DESIRED Y=', desired_arm_y, since_swing)
    swift.set_position(y=desired_arm_y, speed=1000000, wait=True)

    if puck_x > 80 and since_swing >= 20:
        swift.set_position(x=100, relative=True, speed=1000000, wait=True)
        time.sleep(0.3)
        swift.set_position(x=-100, relative=True, speed=1000000, wait=True)
        since_swing = 0

    since_swing += 1

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
