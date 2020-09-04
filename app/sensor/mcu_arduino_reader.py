from datetime import datetime

import smbus2
import struct
import logging
import random

# I2C addressed of Arduinos MCU connected
from ..fds.FdsCommon import FdsCommon as fds
from ..sensor.reader import Reader, SensorValue

TEMP_1_REGISTER = 0x10  # DS18D20 ( onewire, D5 )
TEMP_2_REGISTER = 0x14  # DS18D20 ( onewire, D5 )
TEMP_3_REGISTER = 0x18  # DS18D20 ( onewire, D5 )
PRESSURE_IN_REGISTER = 0x20  # PRESSURE (analog, A1)
PRESSURE_OUT_REGISTER = 0x24  # PRESSURE (analog, A2)
PRESSURE_MIDDLE_REGISTER = 0x28  # PRESSURE (analog, A3)
FLUX_IN_REGISTER = 0x30  # FLUXMETER ( digital input, D2 )
FLUX_OUT_REGISTER = 0x34  # FLUXMETER ( digital input, D3 )
CC_CURRENT_REGISTER = 0x40  # SHUNT  ( LM358 gain 20, analog, A0  )
AC1_CURRENT_REGISTER = 0x44  # SCT013 (analog in A5)
AC2_CURRENT_REGISTER = 0x48  # SCT013 (analog in A5)
DHT11_AIR_REGISTER = 0x50  # DHT11 ( onewire, D6 )
DHT11_HUMIDITY_REGISTER = 0x54  # DHT11 ( onewire, D6 )
FLOODING_STATUS_REGISTER = 0x60  # Flooding sensor ( digital input, D7 )
WATER_LEVEL_REGISTER = 0x70  # DISTANCE ULTRASOUND SENSOR ( software serial, rxD9 txD10 )

TEMP_1_LABEL = fds.LABEL_MCU_TEMP_1  # DS18D20 ( onewire, D5 )
TEMP_2_LABEL = fds.LABEL_MCU_TEMP_2  # DS18D20 ( onewire, D5 )
TEMP_3_LABEL = fds.LABEL_MCU_TEMP_3  # DS18D20 ( onewire, D5 )
PRESSURE_IN_LABEL = fds.LABEL_MCU_PRESSURE_IN  # PRESSURE (analog, A1)
PRESSURE_OUT_LABEL = fds.LABEL_MCU_PRESSURE_OUT  # PRESSURE (analog, A2)
PRESSURE_MIDDLE_LABEL = fds.LABEL_MCU_PRESSURE_MIDDLE  # PRESSURE (analog, A3)
FLUX_IN_LABEL = fds.LABEL_MCU_FLUX_IN  # FLUXMETER ( digital input, D2 )
FLUX_OUT_LABEL = fds.LABEL_MCU_FLUX_OUT  # FLUXMETER ( digital input, D3 )
CC_CURRENT_LABEL = fds.LABEL_MCU_CC_CURRENT  # SHUNT  ( LM358 gain 20, analog, A0  )
AC1_CURRENT_LABEL = fds.LABEL_MCU_AC1_CURRENT  # SCT013 (analog in A6)
AC2_CURRENT_LABEL = fds.LABEL_MCU_AC2_CURRENT  # SCT013 (analog in A7)
DHT11_AIR_LABEL = fds.LABEL_MCU_DHT11_AIR  # DHT11 ( onewire, D6 )
DHT11_HUMIDITY_LABEL = fds.LABEL_MCU_DHT11_HUMIDITY  # DHT11 ( onewire, D6 )
FLOODING_STATUS_LABEL = fds.LABEL_MCU_FLOODING_STATUS  # Flooding sensor ( digital input, D7 )
WATER_LEVEL_LABEL = fds.LABEL_MCU_WATER_LEVEL  # DISTANCE ULTRASOUND SENSOR ( software serial,

# i2c bus number depending on the hardware

DEFAULT_I2C_ADDR = 0x27
SECO_C23_I2C_BUS = 1
UDOO_NEO_I2C_BUS = 3

DEFAULT_I2C_BUS = SECO_C23_I2C_BUS

# data sizes
ARDUINO_FLOAT_SIZE = 4
ARDUINO_INT_SIZE = 2
ARDUINO_DOUBLE_SIZE = 8

DECIMALS = 1


class McuArduinoReader(Reader):

    def __init__(self, id, i2c_bus=DEFAULT_I2C_BUS, i2c_address=DEFAULT_I2C_ADDR, produce_dummy_data=False):

        self.id = id
        self.produce_dummy_data = produce_dummy_data
        self.bus         = None
        self.i2c_bus     = i2c_bus
        self.i2c_address = i2c_address

        if self.produce_dummy_data  == False:
            self.bus = smbus2.SMBus(self.i2c_bus)

    def is_connected(self, arduino_address):
        # print("Arduino ", str(arduinoAddress), " isConnected")
        return True

    def read4_bytes_float(self, dev, start_reg, n_bytes=None):
        value = [0, 0, 0, 0]

        value[0] = self.bus.read_byte_data(dev, start_reg)
        value[1] = self.bus.read_byte_data(dev, start_reg + 1)
        value[2] = self.bus.read_byte_data(dev, start_reg + 2)
        value[3] = self.bus.read_byte_data(dev, start_reg + 3)

        b = struct.pack('4B', *value)
        value = struct.unpack('<f', b)

        return round(value[0], DECIMALS)

    def read2_bytes_integer(self, dev, start_reg, n_bytes=None):
        value = [0, 0]

        value[0] = self.bus.read_byte_data(dev, start_reg)
        value[1] = self.bus.read_byte_data(dev, start_reg + 1)

        b = struct.pack('BB', value[0], value[1])
        value = struct.unpack('<h', b)

        return value[0]

    def read1_byte_boolean(self, dev, start_reg):
        value = self.bus.read_byte_data(dev, start_reg)
        return value

    def generate_dummy(self, values, data):
        for val in values:
            data[val] = round(random.uniform(0, 255), DECIMALS)

    def read(self) -> SensorValue:
        data = self.get_all_data()
        return SensorValue(self.id, data, int(datetime.now().timestamp()))

    # External MCU
    def get_temperature1(self):
        logging.debug("Requested temperature 1")
        value = self.read4_bytes_float(self.i2c_address, TEMP_1_REGISTER, ARDUINO_FLOAT_SIZE)
        return value

    # External MCU
    def get_temperature2(self):
        logging.debug("Requested temperature 2")
        value = self.read4_bytes_float(self.i2c_address, TEMP_2_REGISTER, ARDUINO_FLOAT_SIZE)
        return value

    # External MCU
    def get_temperature3(self):
        logging.debug("Requested temperature 2")
        value = self.read4_bytes_float(self.i2c_address, TEMP_3_REGISTER, ARDUINO_FLOAT_SIZE)
        return value

    def get_pressure_in(self):
        logging.debug("Requested pressure in input")
        value = self.read4_bytes_float(self.i2c_address, PRESSURE_IN_REGISTER, ARDUINO_FLOAT_SIZE)
        return value

    def get_pressure_middle(self):
        logging.debug("Requested pressure in middle")
        value = self.read4_bytes_float(self.i2c_address, PRESSURE_MIDDLE_REGISTER, ARDUINO_FLOAT_SIZE)
        return value

    def get_pressure_out(self):
        logging.debug("Requested pressure in output")
        value = self.read4_bytes_float(self.i2c_address, PRESSURE_OUT_REGISTER, ARDUINO_FLOAT_SIZE)
        return value

    def get_water_flux_in(self):
        logging.debug("Requested water flux in")
        value = self.read2_bytes_integer(self.i2c_address, FLUX_IN_REGISTER, ARDUINO_INT_SIZE)
        return value

    def get_water_flux_out(self):
        logging.debug("Requested water flux ouy")
        value = self.read2_bytes_integer(self.i2c_address, FLUX_OUT_REGISTER, ARDUINO_INT_SIZE)
        return value

    def get_cc_current(self):
        logging.debug("Requested CC current from Shunt")
        value = self.read4_bytes_float(self.i2c_address, CC_CURRENT_REGISTER, ARDUINO_FLOAT_SIZE)
        return value

    def get_ac_current(self, channel):
        logging.debug("Requested AC current from clamp ", str(channel))

        if channel == 1:
            AC_CURRENT_REGISTER = AC1_CURRENT_REGISTER
        elif channel == 2:
            AC_CURRENT_REGISTER = AC2_CURRENT_REGISTER
        else:
            return -1

        value = self.read4_bytes_float(self.i2c_address, AC_CURRENT_REGISTER, ARDUINO_FLOAT_SIZE)

        return value

    def get_dht11_temperature(self):
        logging.debug("Requested internal temperature by DHT11")
        value = self.read4_bytes_float(self.i2c_address, DHT11_AIR_REGISTER, ARDUINO_FLOAT_SIZE)
        return value

    def get_dht11_humidity(self):
        logging.debug("Requested internal temperature by DHT11")
        value = self.read4_bytes_float(self.i2c_address, DHT11_HUMIDITY_REGISTER, ARDUINO_FLOAT_SIZE)
        return value

    def get_flood_status(self):
        logging.debug("Requested flooding status")
        value = self.read1_byte_boolean(self.i2c_address, FLOODING_STATUS_REGISTER)
        return value

    def get_water_level(self):
        logging.debug("Requested tank water level")
        value = self.read2_bytes_integer(self.i2c_address, WATER_LEVEL_REGISTER, ARDUINO_INT_SIZE)
        return value

    def get_all_data(self):
        data = dict()
        #data['timestamp'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        data['type'] = 'mcu'

        if self.produce_dummy_data:
            self.generate_dummy([
                TEMP_1_LABEL,
                TEMP_2_LABEL,
                PRESSURE_IN_LABEL,
                PRESSURE_OUT_LABEL,
                PRESSURE_MIDDLE_LABEL,
                FLUX_IN_LABEL,
                FLUX_OUT_LABEL,
                CC_CURRENT_LABEL,
                AC1_CURRENT_LABEL,
                AC2_CURRENT_LABEL
            ], data)
        else:
            try:
                data[TEMP_1_LABEL] = self.get_temperature1()
                data[TEMP_2_LABEL] = self.get_temperature2()
                data[PRESSURE_IN_LABEL] = self.get_pressure_in()
                data[PRESSURE_OUT_LABEL] = self.get_pressure_middle()
                data[PRESSURE_MIDDLE_LABEL] = self.get_pressure_out()
                data[FLUX_IN_LABEL] = self.get_water_flux_in()
                data[FLUX_OUT_LABEL] = self.get_water_flux_out()
                data[CC_CURRENT_LABEL] = self.get_cc_current()
                data[AC1_CURRENT_LABEL] = self.get_ac_current(1)
                data[AC2_CURRENT_LABEL] = self.get_ac_current(2)
            except Exception as e:
                logging.error('Charge Controller: unpredicted exception')
                print( e )
                raise e

        return data
