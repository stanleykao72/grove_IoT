import time
from grove.grove_relay import GroveRelay

PIN = 5
relay = GroveRelay(PIN)

while True:
    relay.on()
    print('relay.on')
    #time.sleep(1)
    #relay.off()
    #print('relay.off')
    time.sleep(1)
