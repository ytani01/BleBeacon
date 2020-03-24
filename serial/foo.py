#!/usr/bin/env python3
#
#
import serial
import time
import sys

dev_prefix = '/dev/ttyUSB'
speed = 115200

for i in [0, 1, 2]:
    dev = dev_prefix + str(i)
    try:
        ser = serial.Serial(dev, speed, timeout=1)
        break
    except Exception as e:
        print('%s:%s' % (type(e).__name__, e))
        continue

print(ser)
    
while True:
    """
    try:
        ser = serial.Serial(dev, speed, timeout=1)
    except Exception as e:
        print('%s:%s' % (type(e).__name__, e))
        continue
    """
    
    l = ser.readline()
    try:
        l = l.decode('utf-8').replace('\r\n', '')
    except UnicodeDecodeError:
        l = str(l)
        
    if len(l) > 0:
        print('%s' % (l))
        sys.stdout.flush()
        continue

    time.sleep(1)
