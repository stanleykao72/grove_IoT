import time
from grove.i2c import Bus
import RPi.GPIO as GPIO
import smbus2 as smbus

global I2C_ADDRESS
global I2C_SMBUS
global _CMD
global _CMD_CLEAR
global _CMD_WORD
global _CMD_BLOCK
global _REG_CONTROL
global _REG_TIMING
global _REG_ID
global _REG_BLOCKREAD
global _REG_DATA0
global _REG_DATA1
global _POWER_UP
global _POWER_DOWM
global _GAIN_LOW
global _GAIN_HIGH
global _INTEGRATION_START
global _INTEGRATION_STOP
global _INTEGRATE_13
global _INTEGRATE_101
global _INTEGRATE_402
global _INTEGRATE_DEFAULT
global _INTEGRATE_NA
global _GAIN
global _MANUAL
global _INTEG
global _CHANNEL0
global _CHANNEL1
global _D0
global _D1
global _LUX

# bus parameters
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    I2C_SMBUS = 1
else:
    I2C_SMBUS = 0

# Default I2C address
I2C_ADDRESS     = 0x29
# Commands
_CMD            = 0x80
_CMD_CLEAR      = 0x40
_CMD_WORD       = 0x20
_CMD_BLOCK      = 0x10

# Registers
_REG_CONTROL    = 0x00
_REG_TIMING     = 0x01
_REG_ID         = 0x0A
_REG_BLOCKREAD  = 0x0B
_REG_DATA0      = 0x0C
_REG_DATA1      = 0x0E

# Control parameters
_POWER_UP = 0x03
_POWER_DOWN = 0x00

# Testing parameters
ambient         = None
_ambient        = 0
IR              = None
_IR             = 0
_LUX            = None

class Tsl2561:
    i2c = None

    def __init__(self, bus=I2C_SMBUS, address=I2C_ADDRESS, debug=1, pause=0.8):
            # assert(bus is not None)
            # assert(address > 0b000111 and address < 0b1111000)
            self.address = address
            self.bus = Bus(bus)
            self.pause = pause
            self.debug = debug
            self.gain  = 0
            self._bus  = bus
            self._addr = address

            ambient       = None
            IR            = None
            self._ambient = 0
            self._IR      = 0
            self._LUX     = None
            self._control(_POWER_UP)
            self._partno_revision()

    def _reverseByteOrder(self, data):
        """Reverses the byte order of an int (16-bit) or long (32-bit) value"""
        # Courtesy Vishal Sapre
        byteCount = len(hex(data)[2:].replace('L','')[::2])
        val       = 0
        for i in range(byteCount):
           val    = (val << 8) | (data & 0xff)
           data >>= 8
        return val

    def _read_byte(self, address):
        command = _CMD | address
        self.bus.read_byte_data(self.address, command)

    def _read_word(self, address,little_endian=True):
        try:
           command = _CMD | address
           result = self.bus.read_word_data(self.address, command)
           if not little_endian:
               result = ((result << 8) & 0xFF00) + (result >> 8)
           if (self.debug):
               print ("I2C: Device 0x{} returned 0x{} from reg 0x{}".format(self.address, result & 0xFFFF, reg))
           return result
       except IOError, err:
           return self.errMsg()

    def _write_byte(self, address, data):
        command = _CMD | address
        self.bus.write_byte_data(self.address, command, data)

    def _write_word(self, address, data):
        command = _CMD | _AUTO | address
        data = [(data >> 8) & 0xFF, data & 0xFF]
        self.bus.write_i2c_block_data(self.address, command, data)

    def setGain(self, gain = 1):
        """ Set the gain """
        if (gain != self.gain):
            if (gain==1):
                cmd = _CMD | _REG_TIMING
                value = 0x02
                self._write_byte(cmd, value)
                if (self.debug):
                    print ("Setting low gain")
            else:
                cmd = _CMD | _REG_TIMING
                value = 0x12
                self._write_byte(cmd, value)
                if (self.debug):
                    print ("Setting high gain")
            self.gain = gain    # Safe gain for calculation
            print('setGain...gian=',gain)
            time.sleep(self.pause)   # Pause for integration (self.pause must be bigger than integration time)

    def readWord(self, reg):
        """ Reads a word from the TSL2561 I2C device """
        try:
            wordval = self._read_word(reg)
            print ('wordval=',wordval)
            newval = self._reverseByteOrder(wordval)
            print ('newval=',newval)
            if (self.debug):
                print("I2C: Device 0x{}: returned 0x{} from reg 0x{}".format(self._addr, wordval & 0xFFFF, reg))
            return newval
        except IOError:
            print("Error accessing 0x{}: Chcekcyour I2C address".format(self._addr))
            return -1

    def readFull(self, reg = 0x8C):
        """ Read visible + IR diode from the TSL2561 I2C device """
        return self.readWord(reg)

    def readIR(self, reg = 0x8E):
        """ Reads only IR diode from the TSL2561 I2C device """
        return self.readWord(reg)

    def readLux(self, gain = 0):
        """ Grabs a lux reading either with autoranging (gain=0) or with specific gain (1, 16) """
        if (self.debug):
            print ("gain=",gain)
        if (gain == 1 or gain == 16):
            self.setGain(gain)   # Low/High Gain
            ambient = self.readFull()
            IR = self.readIR()
        elif (gain == 0):   # Auto gain
            self.setGain(16)  # First try highGain
            ambient = self.readFull()
            if (ambient < 65535):
                IR = slef.readIR()
            if (ambient >= 65535 or IR >= 65535): # Value(s) exeed(s) datarange
                self.setGain(1)  # Set low Gain
                ambient = self.readFull()
                IR = self.readIR()

        # If either sensor is saturated, no acculate lux value can be achieved.
        if (ambient == 0xffff or IR == 0xffff):
            self._LUX = None
            self._ambient = None
            self._IR = None
            return (self.ambient, self.IR, self._ambient, self._IR, self._LUX)
        if (self.gain == 1):
            self._ambient = 16 * ambient    # Scale 1x to 16x
            self._IR = 16 * IR
        else:
            self._ambient = 1 * ambient
        if (self.debug):
           print ("IR Result without scaling: ",IR)
           print ("IR Result: ", self._IR)
           print ("Ambient Result without scaling: ", ambient)
           print ("Ambient Result: ", self._ambient)

        if (self._ambient == 0):
           # Sometimes, the channel 0 returns 0 when dark ...
           self._LUX = 0.0
           return (ambient, IR, self._ambient, self._IR, self._LUX)
        
        ratio = (self._IR / float(self._ambient)) 

        if (self.debug):
            print ("ratio: ", ratio)

        if ((ratio >= 0) and (ratio <= 0.52)):
            self._LUX = (0.0315 * self._ambient) - (0.0593 * self._ambient * (ratio ** 1.4))
        elif (ratio <= 0.65):
            self._LUX = (0.0229 * self._ambient) - (0.0291 * self._IR)
        elif (ratio <= 0.80):
            self._LUX = (0.0157 * self._ambient) - (0.018 * self._IR)
        elif (ratio <= 1.3):
            self._LUX = (0.00338 * self._ambient) - (0.0026 * self._IR)
        elif (ratio > 1.3):
            self._LUX = 0

        return (ambient, IR, self._ambient, self._IR, self._LUX)
    
    def _control(self, params):
        if (params == _POWER_UP):
            print ("Power ON")
        elif (params == _POWER_DOWN):
            print ("Power OFF")
        cmd = _CMD | _REG_CONTROL | params
        self._write_byte(self._addr, cmd) # select command register and power on
        time.sleep(0.4) # Wait for 400ms to power up or power down.

    def _partno_revision(self):
        """ Read Partnumber and revision of the sensor """
        cmd = _CMD | _REG_ID
        value = self._read_byte(cmd)
        print ("value=",value)
        part = str(value)[7:4]
        if (part == "0000"):
            PartNo = "TSL2560CS"
        elif (part == "0001"):
            PartNo = "TSL2561CS"
        elif (part == "0100"):
            PartNo = "TSL2560T/FN/CL"
        else:
            PartNo = "not TSL2560 or TSL2561"
        RevNo = str(value)[3:0]
        if (self.debug):
            print ("response: ", value)
            print ("PartNo = ", PartNo)
            print ("RevNo = ", RevNo)
        return (PartNo, RevNo)


def main():
    sensor = Tsl2561()
    while (True):
        gain = 0
        val = sensor.readLux(gain)
        ambient = val[0]
        IR = val[1]
        _ambient = val[2]
        _IR = val[3]
        _LUX = val[4]
        if (ambient == 0xffff or IR == 0xffff):
            print ("Sensor is saturated, no lux value can be achieved:")
            print ("ambient = ", ambient)
            print ("IR = ", IR)
            print ("light = ", _LUX)
        elif (_ambient == 0):
            print ("It's dark:")
            print ("ambient = ", ambient)
            print ("_IR =", _IR)
            print ("Light = {} lux.".format(_Lux))
        else:
            print ("There is light:")
            print ("ambient = ", ambient)
            print ("IR = ", IR)
            print ("_ambient = ", _ambient)
            print ("_IR = ", _IR)
            print ("Light = {} lux.".format(_LUX))
        time.sleep(2)
        ambient = None
        IR      = None
        _ambient = 0
        _IR      = 0
        _LUX     = None
        sensor._control(_POWER_DOWN)
    pass

if __name__ == '__main__':
    main()

