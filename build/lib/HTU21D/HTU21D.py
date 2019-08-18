#!/usr/bin/python3

from __future__ import division
import logging
import time
import math
import struct
import array
import time

# The name of this device
_DEFAULT_NAME = "HTU21D"

# HTU21D default address.
HTU21D_I2CADDR           = 0x40

# Commands
HTU21D_READTEMPHOLD      = 0xE3 # Trigger temperature measurement
HTU21D_READHUMHOLD       = 0xE5 # Trigger humidity measurement
HTU21D_READTEMPNOHOLD    = 0xF3 # Trigger temperature measurement no hold master
HTU21D_READHUMNOHOLD     = 0xF5 # Trigger humidyt measurement no hold master
HTU21D_WRITEUSERREG      = 0xE6 # Write user register
HTU21D_READUSERREG       = 0xE7 # Read user register
HTU21D_SOFTRESET         = 0xFE # Soft reset
#
# HOLD: serial clock is held until conversion completed, disabling other communcation in i2c
# NO HOLD: serial clock is free
# In NO HOLD option, the MCU needs to poll the sensor for termination and sensor will 
# acknowldege read request if conversion is completed

# define the class that encapsulates the device being created. All information associated with this
# device is encapsulated by this class. The device class should be the only value exported

class HTU21D(object):
    device_name         =_DEFAULT_NAME
    
    # Constructor
    def __init__(self, i2c=None, busnum=None, logger='HTU21D.HTU21D', **kwargs):
        self._logger = logging.getLogger(logger)
        # Create I2C device.
        if i2c is None:
            import Adafruit_GPIO.I2C as i2c
        self._device = i2c.get_i2c_device(HTU21D_I2CADDR, **kwargs)
        # program user register if necessary
        # default is 12bit RH and 14 bit Temp
        # default is VDD>2.25, On Chip heater off, OTP reload disabled
        self._temperature = -255
        self._humitidy = -255
        self._ok = self._soft_reset()
        if self._ok:
            self.update()

    def _soft_reset(self):
        try:
            self._device.writeRaw8(HTU21D_SOFTRESET)  #Reset device
            time.sleep(0.05) # give some time to recover, should take less than 15ms
            return True
        except OSError as exc:
            self._logger.error("Bad writing in bus: %s", exc)
            return False

    @staticmethod        
    def _calc_temp(sensor_temp):
        t_sensor_temp = sensor_temp / 65536.0
        return -46.85 + (175.72 * t_sensor_temp)

    @staticmethod
    def _calc_humid(sensor_humid):
        t_sensor_humid = sensor_humid / 65536.0
        return -6.0 + (125.0 * t_sensor_humid)

    @staticmethod
    def _temp_coefficient(rh_actual, temp_actual):
        return rh_actual - (25.0 - temp_actual) * 0.15

    @staticmethod
    def _crc8check(value):
        # Ported from Sparkfun Arduino HTU21D Library:
        # https://github.com/sparkfun/HTU21D_Breakout
        remainder = ((value[0] << 8) + value[1]) << 8
        remainder |= value[2]

        # POLYNOMIAL = 0x0131 = x^8 + x^5 + x^4 + 1 divisor =
        # 0x988000 is the 0x0131 polynomial shifted to farthest
        # left of three bytes
        divisor = 0x988000

        for i in range(0, 16):
            if(remainder & 1 << (23 - i)):
                remainder ^= divisor
            divisor = divisor >> 1

        if remainder == 0:
            return True
        else:
            return False

    @property
    def sample_ok(self):
        """Return True for a valid measurement data."""
        return self._ok and self._temperature > -100 and self._humidity > -1

    def dewpoint(self, temp, humid):
        A=8.1332
        B=1762.39
        C=235.66
        PP=math.pow(10, A-(B/(temp+C)) )
        return -(C + B/(math.log10(humid*PP/100)-A))

    def update(self):
        """Read raw data and calculate temperature and humidity."""
        if not self._ok:
            self._logger.error("Trying to restore with soft reset")
            self._ok = self._soft_reset()
        try:
            self._device.writeRaw8(HTU21D_READTEMPNOHOLD)  # Measure temp
            time.sleep(.050) # 50ms max for 14bits
            data = self._device.readRawList(3)
            buf_t = array.array('B', data)
            
            self._device.writeRaw8(HTU21D_READHUMNOHOLD)  # Measure humidity
            time.sleep(.016) # 16ms max for 12bits
            data = self._device.readRawList(3)
            buf_h = array.array('B', data)
        except OSError as exc:
            self._ok = False
            self._logger.error("Bad reading: %s", exc)
            return

        if self._crc8check(buf_t):
            temp = (buf_t[0] << 8 | buf_t[1]) & 0xFFFC
            self._logger.debug('Raw temp {0} C'.format(temp))
            self._temperature = self._calc_temp(temp)

            if self._crc8check(buf_h):
                humid = (buf_h[0] << 8 | buf_h[1]) & 0xFFFC
                rh_actual = self._calc_humid(humid)
                # For temperature coefficient compensation
                rh_final = self._temp_coefficient(rh_actual, self._temperature)
                rh_final = 100.0 if rh_final > 100 else rh_final  # Clamp > 100
                rh_final = 0.0 if rh_final < 0 else rh_final  # Clamp < 0
                self._logger.debug('Calibrated humidity {0} %H'.format(rh_final))
                self._humidity = rh_final
            else:
                self._humidity = -255
                self._ok = False
                self._logger.error("Bad CRC error with humidity")
                self._logger.error('Raw temp {0} C'.format(buf_h))
        else:
            self._temperature = -255
            self._ok = False
            self._logger.error("Bad CRC error with temperature")
            self._logger.error('Raw temp {0} C'.format(buf_t))

    def read_temperature(self):
        self._device.writeRaw8(HTU21D_READTEMPNOHOLD)  # Measure temp
        time.sleep(.050) # 50ms max for 14bits
        data = self._device.readRawList(3)
        buf = array.array('B', data)
        if self._crc8check(buf):
            temp = (buf[0] << 8 | buf[1]) & 0xFFFC
            self._logger.debug('Raw temp {0} C'.format(temp))
            return self._calc_temp(temp)
        else:
            self._logger.debug('Raw temp {0} C'.format(-255))
            return -255

    def read_humidity(self):
        temp_actual = self.read_temperature()  # For temperature coefficient compensation
        self._device.writeRaw8(HTU21D_READHUMNOHOLD)  # Measure humidity
        time.sleep(.016) # 16ms max for 12bits
        data = self._device.readRawList(3)
        buf = array.array('B', data)
        if self._crc8check(buf):
            humid = (buf[0] << 8 | buf[1]) & 0xFFFC
            rh_actual = self._calc_humid(humid)
            rh_final = self._temp_coefficient(rh_actual, temp_actual)
            rh_final = 100.0 if rh_final > 100 else rh_final  # Clamp > 100
            rh_final = 0.0 if rh_final < 0 else rh_final  # Clamp < 0
            self._logger.debug('Calibrated humidity {0} %H'.format(rh_final))
            return (rh_final, temp_actual)
        else:
            self._logger.debug('Calibrated humidity {0} %H'.format(-255))
            return (-255, temp_actual)

    @property
    def temperature(self):
        """Return temperature in celsius."""
        return self._temperature

    @property
    def humidity(self):
        """Return relative humidity in percentage."""
        return self._humidity