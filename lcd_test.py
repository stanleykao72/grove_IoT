import sys
import time

from grove.factory import Factory
from grove.grove_relay import GroveRelay
from grove.adc import ADC
from statistics import mean

PIN = 22 # relay PIN
relay = GroveRelay(PIN)
adc = ADC()
print("name: {0:20}, version: {1:4}".format(adc.name, adc.version))

# LCD 16x2 Characters
# lcd = Factory.getDisplay("JHD1802")
lcd = Factory.getLcd("JHD1802")
rows, cols = lcd.size()
print("LCD model: {}".format(lcd.name))
print("LCD type : {} x {}".format(cols, rows))
lcd.setCursor(0, 0)

# ph = (voltage - b)/a
a = (2.5-3.0)/(7.0-4.01)
b = 2.5 - a*7.0
offset = 0.0283
n = 1000

# ds18b20 sensor id
_serialnum = "28-00000b702a1d"

try:
    print('按下 Ctrl-C 可停止程式')
    lcd.clear()
    while True:
       lcd.setCursor(0, 0)
       lcd.write("Date: {}".format(time.strftime("%Y/%m/%d")))
       lcd.setCursor(1, 0)
       lcd.write("Time: {}".format(time.strftime("%H:%M:%S")))
       # read sensor data
       voltage = []
       temp_list = []
       for i in range(1000):
           # get voltage from PH sensor
           voltage.append(adc.read_voltage(0)/1000)
       for i in range(5):
           # get temperature
           filename="/sys/bus/w1/devices/"+_serialnum+"/w1_slave"
           tfile= open(filename)
           text = tfile.read()
           tfile.close()
           secondline = text.split("\n")[1]
           temperaturedata= secondline.split(" ")[9]
           global temperature
           temperature = float(temperaturedata[2:])
           temperature = temperature / 1000
           temp_list.append(temperature)
           # print ('temperature:',temperature)
           firstline = text
           ccrrcc = firstline.split(" ")[11]
           ccrrcc = (ccrrcc[:3]) #take only first 3 characters
           global noflag
           noflag = 0
           if ccrrcc != 'YES':
              print (' Oops the sensor is missing')
              
       ph = round((mean(voltage) - b - offset)/a,2)
       print("ph:{0:>6}, voltage:{1:>6} ".format(ph, mean(voltage)))
       lcd.setCursor(0, 0)
       lcd.write("PH:{0}, V:{1}".format(ph, mean(voltage)))
       lcd.setCursor(1, 0)
       print("temperature:{}".format(mean(temp_list)))
       lcd.write("Temp:{:<11}".format(mean(temp_list)))
       # relay.on()
       # lcd.write("Relay ON!")
       # lcd.setCursor(1, cols - 1)
       # lcd.write('X')
       # lcd.setCursor(rows - 1, 0)
       
       time.sleep(3)
       # relay.off()
       lcd.setCursor(1, 0)
       lcd.write("Relay OFF!")
       time.sleep(1)

except KeyboardInterrupt:
    lcd.backlight_enabled=False
    print('關閉程式')
finally:
    lcd.clear()
