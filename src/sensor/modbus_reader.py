from datetime import datetime

import smbus2
import struct
import logging
import random

from pymodbus.exceptions import ModbusIOException
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

# I2C addressed of Arduinos MCU connected
import fds.FdsCommon as fds
from sensor.reader import Reader
from sensor.reader import SensorValue


DEFAULT_CHARGE_CONTROLLER_UNIT = 0x01
DEFAULT_RELAY_BOX_UNIT         = 0x09
DEFAULT_MODBUS_PORT            = 502

DEFAULT_MODBUS_IP            = '192.168.2.253'
DEFAULT_C23_RS485            = '/dev/ttymxc2'  # mxc3 on schematics

# Modbus reader
class ModbusChargeControllerReader(Reader):

    def __init__(self,
                 id,
                 ip_address = DEFAULT_MODBUS_IP,
                 unit_id    = DEFAULT_CHARGE_CONTROLLER_UNIT,
                 produce_dummy_data = False):

        self.id                 = id
        self.ip_address         = ip_address
        self.unit_id            = unit_id
        self.produce_dummy_data = produce_dummy_data
        self.client             = None


    def connect(self):
        try:
            print("Connect modbus...")
            self.client = ModbusClient(self.ip_address, DEFAULT_MODBUS_PORT)
            self.client.connect()
        except Exception as e:
            err = 'Error in Modbus Connect: ' + str(e)
            self.client = None
            print( err )


    def generate_dummy(self, values, data):
        for val in values:
            data[val] = random.uniform(0, 60)

    def get_charge_controller_data(self):
        data = {'type': 'charge_controller'}

        if self.produce_dummy_data == True:
            self.generate_dummy([
                fds.LABEL_CC_BATTS_V,
                fds.LABEL_CC_BATT_SENSED_V,
                fds.LABEL_CC_BATTS_I,
                fds.LABEL_CC_ARRAY_V,
                fds.LABEL_CC_ARRAY_I,
                fds.LABEL_CC_STATENUM,
                fds.LABEL_CC_HS_TEMP,
                fds.LABEL_CC_RTS_TEMP,
                fds.LABEL_CC_OUT_POWER,
                fds.LABEL_CC_IN_POWER,
                fds.LABEL_CC_MINVB_DAILY,
                fds.LABEL_CC_MAXVB_DAILY,
                fds.LABEL_CC_MINTB_DAILY,
                fds.LABEL_CC_MAXTB_DAILY,
            ], data)

            data[fds.LABEL_CC_DIPSWITCHES] = bin(0x02)[::-1][:-2].zfill(8)
        else:
            try:
                print('sono entrato dio merdoso!')
                self.connect()
                # read registers. Start at 0 for convenience
                rr = self.client.read_holding_registers(0, 80, unit=self.unit_id)

                # for all indexes, subtract 1 from what's in the manual
                V_PU_hi = rr.registers[0]
                V_PU_lo = rr.registers[1]
                I_PU_hi = rr.registers[2]
                I_PU_lo = rr.registers[3]

                V_PU = float(V_PU_hi) + float(V_PU_lo)
                I_PU = float(I_PU_hi) + float(I_PU_lo)

                v_scale = V_PU * 2**(-15)
                i_scale = I_PU * 2**(-15)
                p_scale = V_PU * I_PU * 2**(-17)

                # battery sense voltage, filtered
                data[fds.LABEL_CC_BATTS_V] = rr.registers[24] * v_scale
                data[fds.LABEL_CC_BATT_SENSED_V] = rr.registers[26] * v_scale
                data[fds.LABEL_CC_BATTS_I]     = rr.registers[28] * i_scale
                data[fds.LABEL_CC_ARRAY_V]     = rr.registers[27] * v_scale
                data[fds.LABEL_CC_ARRAY_I]     = rr.registers[29] * i_scale
                data[fds.LABEL_CC_STATENUM]    = rr.registers[50]
                data[fds.LABEL_CC_HS_TEMP]     = rr.registers[35]
                data[fds.LABEL_CC_RTS_TEMP]    = rr.registers[36]
                data[fds.LABEL_CC_OUT_POWER]   = rr.registers[58] * p_scale
                data[fds.LABEL_CC_IN_POWER]    = rr.registers[59] * p_scale
                data[fds.LABEL_CC_MINVB_DAILY] = rr.registers[64] * v_scale
                data[fds.LABEL_CC_MAXVB_DAILY] = rr.registers[65] * v_scale
                data[fds.LABEL_CC_MINTB_DAILY] = rr.registers[71]
                data[fds.LABEL_CC_MAXTB_DAILY] = rr.registers[72]
                data[fds.LABEL_CC_DIPSWITCHES] = bin(rr.registers[48])[::-1][:-2].zfill(8)
                # led_state            = rr.registers
            except ModbusIOException as e:
                logging.error('Charge Controller: modbusIOException')
                raise e
            except Exception as e:
                logging.error('Charge Controller: unpredicted exception')
                raise e

        return data


    def read(self) -> SensorValue:
        data = self.get_charge_controller_data()
        return SensorValue(self.id, data, int(datetime.now().timestamp()))






# Modbus reader
class ModbusRelayBoxReader(Reader):

    def __init__(self,
                 id,
                 ip_address = DEFAULT_MODBUS_IP,
                 unit_id    = DEFAULT_RELAY_BOX_UNIT,
                 produce_dummy_data = False):

        self.id                 = id
        self.ip_address         = ip_address
        self.unit_id            = unit_id
        self.produce_dummy_data = produce_dummy_data
        self.client             = None

    def connect(self):
        try:
            print("Connect modbus...")
            self.client = ModbusClient(self.ip_address, DEFAULT_MODBUS_PORT)
            self.client.connect()
        except Exception as e:
            err = 'Error in Modbus Connect: ' + str(e)
            self.client = None
            print( err )


    def generate_dummy(self, values, data):
        for val in values:
            data[val] = random.uniform(0, 60)



    def get_relay_box_data(self):
        data = {'type': 'relay_box'}

        if self.produce_dummy_data == True:
            self.generate_dummy([
                fds.LABEL_RB_VB,
                fds.LABEL_RB_ADC_VCH_1,
                fds.LABEL_RB_ADC_VCH_2,
                fds.LABEL_RB_ADC_VCH_3,
                fds.LABEL_RB_ADC_VCH_4,
                fds.LABEL_RB_T_MOD,
                fds.LABEL_RB_GLOBAL_FAULTS,
                fds.LABEL_RB_GLOBAL_ALARMS,
                fds.LABEL_RB_HOURMETER_HI,
                fds.LABEL_RB_HOURMETER_LO,
                fds.LABEL_RB_CH_FAULTS_1,
                fds.LABEL_RB_CH_FAULTS_2,
                fds.LABEL_RB_CH_FAULTS_3,
                fds.LABEL_RB_CH_FAULTS_4,
                fds.LABEL_RB_CH_ALARMS_1,
                fds.LABEL_RB_CH_ALARMS_2,
                fds.LABEL_RB_CH_ALARMS_3,
                fds.LABEL_RB_CH_ALARMS_4
            ], data)

            data[fds.LABEL_CC_DIPSWITCHES] = bin(0x02)[::-1][:-2].zfill(8)

        else:
            try:
                self.connect()
                # read registers. Start at 0 for convenience
                rr = self.client.read_holding_registers(0, 18, unit=self.unit_id)
                v_scale = float(78.421 * 2 ** (-15))

                data[fds.LABEL_RB_VB] = rr.registers[0] * v_scale
                data[fds.LABEL_RB_ADC_VCH_1] = rr.registers[1] * v_scale
                data[fds.LABEL_RB_ADC_VCH_2] = rr.registers[2] * v_scale
                data[fds.LABEL_RB_ADC_VCH_3] = rr.registers[3] * v_scale
                data[fds.LABEL_RB_ADC_VCH_4] = rr.registers[4] * v_scale
                data[fds.LABEL_RB_T_MOD] = rr.registers[5]
                data[fds.LABEL_RB_GLOBAL_FAULTS] = rr.registers[6]
                data[fds.LABEL_RB_GLOBAL_ALARMS] = rr.registers[7]
                data[fds.LABEL_RB_HOURMETER_HI] = rr.registers[8]
                data[fds.LABEL_RB_HOURMETER_LO] = rr.registers[9]
                data[fds.LABEL_RB_CH_FAULTS_1] = rr.registers[10]
                data[fds.LABEL_RB_CH_FAULTS_2] = rr.registers[11]
                data[fds.LABEL_RB_CH_FAULTS_3] = rr.registers[12]
                data[fds.LABEL_RB_CH_FAULTS_4] = rr.registers[13]
                data[fds.LABEL_RB_CH_ALARMS_1] = rr.registers[14]
                data[fds.LABEL_RB_CH_ALARMS_2] = rr.registers[15]
                data[fds.LABEL_RB_CH_ALARMS_3] = rr.registers[16]
                data[fds.LABEL_RB_CH_ALARMS_4] = rr.registers[17]
                # led_state            = rr.registers
            except ModbusIOException as e:
                logging.error('Relay Box: modbusIOException')
                raise e
            except Exception as e:
                logging.error('Relay Box: unpredicted exception')
                raise e

        return data


    def read(self) -> SensorValue:
        data = self.get_relay_box_data()
        return SensorValue(self.id, data, int(datetime.now().timestamp()))


    def disconnect(self):
        try:
            self.client.disconnect()
        except Exception as e:
            err = 'Error in Modbus Disconnect: ' + str(e)
            print( err )
        finally:
            self.client = None
