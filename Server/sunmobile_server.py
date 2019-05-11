import socket
import argparse
import time
import os
import requests
import RPi.GPIO as GPIO
import cv2
import numpy as np
cap = cv2.VideoCapture(0)

beep = 16

L_power = 3
L_front = 2
L_reverse = 4

R_power = 17
R_front = 22
R_reverse = 27


#set GPIO Pins
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 18
GPIO_ECHO = 23
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
normalDistance = 15

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def setup_gpio():
    os.system("sudo pigpiod")  # Launching GPIO library
    time.sleep(1)  # As i said it is too impatient and so if this delay is removed you will get an error
    import pigpio
    pi = pigpio.pi()
    toZero(pi)
    time.sleep(1)

    return pi

def toZero(pi):
    pi.write(L_power, 0)
    pi.write(R_power, 0)
    pi.write(L_front, 0)
    pi.write(L_reverse, 0)
    pi.write(R_front, 0)
    pi.write(R_reverse, 0)

def control(pi,speed,L_front_enable, L_reverse_enable, R_front_enable, R_reverse_enable):
    toZero(pi)
    if(L_front_enable == True):
        pi.write(L_reverse, 0)
        pi.write(L_front, 1)
    if(L_reverse_enable == True):
        pi.write(L_front, 0)
        pi.write(L_reverse, 1)
    if(L_front_enable == True) or (L_reverse_enable == True):
        pi.set_PWM_dutycycle(L_power, speed)
    if(R_front_enable == True):
        pi.write(R_reverse, 0)
        pi.write(R_front, 1)
    if(R_reverse_enable == True):
        pi.write(R_front, 0)
        pi.write(R_reverse, 1)
    if(R_front_enable == True) or (R_reverse_enable == True):
        pi.set_PWM_dutycycle(R_power, speed)

def go_forward(pi, speed):
    control(pi, speed, True, False, True, False)

def go_reverse(pi, speed):
    control(pi, speed, False, True, False, True)

def go_right(pi, speed):
    control(pi, speed, True, False, False, True)

def go_left(pi, speed):
    control(pi, speed, False, True, True, False)

def setup_socket(port):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('', port)
    sock.bind(server_address)
    sock.listen(1)

    return sock


def get_parameters(sock):
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        data = connection.recv(32)
        mode, direction, speed = convert_to_signals(data)
        return mode, direction,speed
    except requests.ConnectionError:
        print("connection is empty")
    finally:
        # Clean up the connection
        connection.close()


def convert_to_signals(data):
    data_arr = data.decode().split("/")
    # conn.send(data.upper())
    data_arr = list(map(int, data_arr))
    mode = data_arr[0]
    direction = data_arr[1]
    speed = data_arr[2]
    return mode, direction,speed

def super_exit(pi, sock):
    toZero(pi)
    GPIO.cleanup()
    sock.close()
    exit()

def goByDirection(pi, speed, direction):
        if direction == 0:
            toZero(pi)
        if direction == 1:
            go_left(pi, speed)
        if direction == 2:
            go_forward(pi, speed)
        if direction == 3:
            go_right(pi, speed)
        if direction == 4:
            go_reverse(pi, speed)

def goSecurity(pi, speed, direction):
    goByDirection(pi, speed, direction)
    dist = distance()
    print(dist)
    while(dist > normalDistance):
        print(dist)
        dist = distance()
    control(pi, 0, False, False, False, False)

def bokomRight(pi, speed):
    toZero(pi)
    pi.write(L_front, 1)
    pi.write(L_power, 0)
    pi.write(R_reverse, 1)
    pi.set_PWM_dutycycle(R_power, 255)

def bokomLeft(pi, speed):
    toZero(pi)
    pi.write(L_reverse, 1)
    pi.set_PWM_dutycycle(L_power, 255)
    pi.write(R_front, 1)
    pi.write(R_power, 0)

def goAutopilot(pi, speed):
    img_size = [200, 360]

    src = np.float32([[20, 200],
                      [340, 200],
                      [340, 180],
                      [20, 180]])

    src_draw = np.array(src, dtype=np.int32)

    dst = np.float32([[0, img_size[0]],
                      [img_size[1], img_size[0]],
                      [img_size[1], 0],
                      [0, 0]])

    while (cv2.waitKey(1) != 27):
        ret, frame = cap.read()
        if ret == False:
        #  print("End of video")
            break

        resized = cv2.resize(frame, (img_size[1], img_size[0]))
        #cv2.imshow("frame", resized)

        r_channel = resized[:, :, 2]
        binary = np.zeros_like(r_channel)
        binary[(r_channel > 200)] = 1  # 255
        #cv2.imshow("r_channel",binary)

        hls = cv2.cvtColor(resized, cv2.COLOR_BGR2HLS)
        s_channel = resized[:, :, 2]
        binary2 = np.zeros_like(s_channel)
        binary2[(r_channel > 160)] = 1

        allBinary = np.zeros_like(binary)
        allBinary[((binary == 1) | (binary2 == 1))] = 255
        #cv2.imshow("binary", allBinary)

        allBinary_visual = allBinary.copy()
        cv2.polylines(allBinary_visual, [src_draw], True, 255)
        #cv2.imshow("polygon", allBinary_visual)

        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(allBinary, M, (img_size[1], img_size[0]), flags=cv2.INTER_LINEAR)
        d1 = np.sum(warped[150:160, 270:280])
        d2 = np.sum(warped[150:160, 290:300])
        d3 = np.sum(warped[150:160, 310:320])
        if (d1>400):
            d1 = 1
        else:
            d1 = 0
        if (d2>400):
            d2 = 1
        else:
            d2 = 0
        if (d3 > 400):
            d3 = 1
        else:
            d3 = 0
        #print(d1,"  ",d2,"  ",d3)
        if (d1==0) and (d2==0) and (d3==1):
            go_right(pi, speed)
        elif (d1==1) and (d2==0) and (d3==0):
            go_left(pi, speed)
        elif (d1==0) and (d2==1) and (d3==0):
            go_forward(pi, speed)
        else:
            go_forward(pi, speed)



def main():

    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", required=False,
                    help="choose port: 1080 as default")
    ap.add_argument("-c", "--calibrate", required=False,
                    help="car motor calibration")
    args = vars(ap.parse_args())

    port = 1080
    if args["port"] is not None:
        if int(args["port"]):
            port = (int(args["port"]))

    pi = setup_gpio()
    toZero(pi)

    sock = setup_socket(port)

    if args["calibrate"] is not None:
        if int(args["calibrate"])==1:
            calibrate(pi,ESC)
        if int(args["calibrate"])==0:
            pass

    while True:

        mode, direction, speed = get_parameters(sock)
        print(mode, direction)

        if mode == 1:
            goSecurity(pi, speed, direction)
        elif mode == 0:
            goByDirection(pi, speed, direction)
        elif mode == -1:
            super_exit(pi, sock)
        elif mode == 2:
            goAutopilot(pi, speed)
        elif mode == 3:
            if direction == 1:
                    bokomLeft(pi, speed)
            elif direction == 3:
                    bokomRight(pi, speed)

if __name__ == '__main__':
    main()