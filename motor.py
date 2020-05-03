import time
from grove.grove_i2c_motor_driver import MotorDriver
import datetime


def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()

addml = 5  # add 5 ml
addinterval = addml*30

motor1 = MotorDriver(address=0x0f)
#motor2 = MotorDriver(address=0x0f)

try:
    print("time Begin = {}".format(time.strftime("%H:%M:%S")))
    t1 = datetime.datetime.now().time()
    t2 = addSecs(t1, addinterval)
    while datetime.datetime.now().time() < t2:
        # speed range: 0(lowest) - 100(fastest)
        # motor.set_speed(100)
        # channel 1 only
        # to set channel 1&2: motor.set_speed(100, 100)

        # direction: True(clockwise), False(anti-clockwise)
        motor1.set_dir(True,True)
        #motor2.set_dir(True,False)
        # channel 1 only,
        # to set channel 1&2: motor.set_dir(True, True)

        # time.sleep(2)

        motor1.set_speed(20,20)
        #motor2.set_speed(100,0)
        # motor.set_dir(False)
        time.sleep(1)
    # motor1.set_speed(0,0)
    print("time End = {}".format(time.strftime("%H:%M:%S")))
except KeyboardInterrupt:
    # motor1.set_speed(0,0)
    print("time Interrupt = {}".format(time.strftime("%H:%M:%S")))

