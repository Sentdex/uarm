'''
Might help to always put arm back to some level or even to let it sit
at x=0 always? not sure. Could also constantly reset the X to 82 or whatever
'''


import cv2
import numpy as np
from uf.wrapper.swift_api import SwiftAPI
import time

# what's the maximum in positive that the arm can do?
ARM_Y_MAX = 190

RESCALE_FACTOR = 1.0
cap = cv2.VideoCapture(1)
#set cv2 frame buffer to 1
cap.set(cv2.CAP_PROP_BUFFERSIZE,1)

WIDTH = int(1280*RESCALE_FACTOR)
HEIGHT = int(720*RESCALE_FACTOR)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

H_min = 0
S_min = 60
V_min = 120
H_max = 10
S_max = 255
V_max = 255

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
swift_r = swift.set_gripper(True)
swift.set_position(x=200, y=0, z=5, relative=False, speed=20000, wait=True)
swift_r = swift.send_cmd_sync("M204 P700 R700 T700\n")
swift.set_position(x=200, y=0, z=3, relative=False, speed=20000, wait=True)


for i in range(15):
    _, frame = cap.read()

#r = cv2.selectROI(frame)
#print(r)
#time.sleep(555)

if RESCALE_FACTOR == 0.5:
    r = (66, 21, 560, 270)
elif RESCALE_FACTOR == 1.0:
    r = (104, 36, 1136, 557)

# so it doesnt keep swinging to hit puck:
since_swing = 9999
move_count = 0

while(1):
    ret, image = cap.read()
    image2 = image[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    frame_to_thresh = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)

    thresh = cv2.inRange(
        frame_to_thresh, (H_min, S_min, V_min), (H_max, S_max, V_max))

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(
        mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > (RESCALE_FACTOR*20) and radius < (RESCALE_FACTOR*50): #  adding the less than part too.
            #print(radius)
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(image2, (int(x), int(y)),
                       int(radius), (0, 255, 255), 2)
            cv2.circle(image2, center, 3, (0, 0, 255), -1)
            cv2.putText(image2, "centroid", (center[
                        0] + 10, center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            cv2.putText(image2, "(" + str(center[0]) + "," + str(center[1]) + ")", (center[
                        0] + 10, center[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)


            cropped_height, cropped_width, channels = image2.shape
            puck_x = center[0]/cropped_width
            puck_y = center[1]/cropped_height

            # get the actual desired y position
            desired_arm_y = (puck_y*(ARM_Y_MAX*2))-ARM_Y_MAX
            print(desired_arm_y)

            swift.set_position(y=round(desired_arm_y, 2), x=200, speed=30000)

            print(puck_x)
            if puck_x > 0.80 and puck_x < 0.94 and since_swing >= 20:
                #swift_r = swift.send_cmd_sync("M204 P5000 R5000 T5000\n")
                swift.set_position(x=40, z=-0.5, relative=True, speed=1000000, wait=True)
                #swift_r = swift.send_cmd_sync("M204 P600 R600 T600\n")
                swift.set_position(x=-40, relative=True, speed=30000)
                since_swing = 0
                swift.set_servo_angle(3, 90)
            since_swing += 1


    # show the frame to our screen
    cv2.imshow("Original", image)
    #cv2.imshow("Marked", image2)

    if cv2.waitKey(1) & 0xFF is ord('q'):
        break
