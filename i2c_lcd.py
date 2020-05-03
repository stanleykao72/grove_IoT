import sys
import time
import smbus2
from RPLCD.i2c import CharLCD
from grove.adc import ADC

sys.path.insert(0,"grove.py")
print(sys.path)
sys.modules['smbus'] = smbus2

lcd = CharLCD('PCF8574', address=0x27, port=1, backlight_enabled=True)
adc = ADC()
Offset = -2.2 

print("name: {0:20}, version: {1:4}".format(adc.name, adc.version))

try:
    print('按下 Ctrl-C 可停止程式')
    lcd.clear()
    while True:
        lcd.cursor_pos = (0, 0)
        lcd.write_string("Date: {}".format(time.strftime("%Y/%m/%d")))
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Time: {}".format(time.strftime("%H:%M:%S")))
        #voltage = adc.read_voltage(0)/1000
        raw = adc.read_raw(0)
        voltage = adc.read_voltage(0)
        percent = adc.read(0)
        print ("raw:{0:>6}, voltage:{1:>6}, percent(%):{2:>6} ".format(raw, voltage, percent))
        # phValue = 7.0 + (voltage - 3.2) * (-5.5)
        # phValue= voltage*5.0/1024/6
        # phValue=3.5*phValue+Offset
        # print(voltage, phValue)
        time.sleep(1)

except KeyboardInterrupt:
    lcd.backlight_enabled=False
    print('關閉程式')
finally:
    lcd.clear()
