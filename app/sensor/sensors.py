import configparser
import json
import os
from time import sleep

from . import modbus_reader, mcu_arduino_reader
from ..utils import IIoT


class Sensors:

    def __init__(self, config_file, mqtt_client):

        self.configurations = {}
        self.charge_controller = None
        self.charge_controller_2 = None
        self.relay_box = None
        self.mcu = None
        self.mqtt_client = mqtt_client
        self.config_file = config_file

    def init_properties(self):
        configs = configparser.ConfigParser()
        configs.read(self.config_file)

        if not configs.has_option('DEFAULT', 'READING_INTERVAL'):
            self.read_properties_from_env()
        else:
            self.read_properties(configs)

    def read_properties_from_env(self):
        self.configurations['READING_INTERVAL'] = int(os.getenv('READING_INTERVAL', 10))
        self.configurations['DUMMY_DATA'] = bool(os.getenv('DUMMY_DATA', False))
        self.configurations['MODBUS_IP'] = os.getenv('MODBUS_IP', '192.168.2.253')
        self.configurations['CHARGE_CONTROLLER_1_MODBUS_UNIT'] = os.getenv('CHARGE_CONTROLLER_1_MODBUS_UNIT',
                                                                           None)  # 0x1
        self.configurations['CHARGE_CONTROLLER_2_MODBUS_UNIT'] = os.getenv('CHARGE_CONTROLLER_2_MODBUS_UNIT', None)
        self.configurations['RELAY_BOX_MODBUS_UNIT'] = os.getenv('RELAY_BOX_MODBUS_UNIT', None)  # 0x09
        self.configurations['MCU_I2C_CHANNEL'] = os.getenv('MCU_I2C_CHANNEL', 1)
        self.configurations['MCU_ARDUINO_I2C_ADDRESS'] = os.getenv('MCU_ARDUINO_I2C_ADDRESS', None)  # 0x27

    def read_properties(self, configs):
        default = configs['DEFAULT']
        self.configurations['READING_INTERVAL'] = int(default['READING_INTERVAL'])
        self.configurations['MODBUS_IP'] = default['MODBUS_IP']
        self.configurations['CHARGE_CONTROLLER_1_MODBUS_UNIT'] = default['CHARGE_CONTROLLER_1_MODBUS_UNIT']
        self.configurations['CHARGE_CONTROLLER_2_MODBUS_UNIT'] = default['CHARGE_CONTROLLER_2_MODBUS_UNIT']
        self.configurations['RELAY_BOX_MODBUS_UNIT'] = default['RELAY_BOX_MODBUS_UNIT']
        self.configurations['MCU_I2C_CHANNEL'] = default['MCU_I2C_CHANNEL']
        self.configurations['MCU_ARDUINO_I2C_ADDRESS'] = default['MCU_ARDUINO_I2C_ADDRESS']
        self.configurations['DUMMY_DATA'] = bool(default['DUMMY_DATA'])

    def get_properties(self):
        return self.configurations

    def init_sensors(self):
        if self.configurations['CHARGE_CONTROLLER_1_MODBUS_UNIT'] is not None:
            try:
                self.charge_controller = modbus_reader.ModbusChargeControllerReader(
                    'cc1',
                    unit_id=int(self.configurations['CHARGE_CONTROLLER_1_MODBUS_UNIT']),
                    produce_dummy_data=self.configurations['DUMMY_DATA']
                )
            except Exception as e:
                print(e)
                self.charge_controller = None
        else:
            self.charge_controller = None

        if self.configurations['CHARGE_CONTROLLER_2_MODBUS_UNIT'] is not None:
            try:
                self.charge_controller_2 = modbus_reader.ModbusChargeControllerReader(
                    'cc2',
                    unit_id=int(self.configurations['CHARGE_CONTROLLER_2_MODBUS_UNIT']),
                    produce_dummy_data=self.configurations['DUMMY_DATA']
                )
            except Exception as e:
                print(e)
                self.charge_controller_2 = None
        else:
            self.charge_controller_2 = None

        if self.configurations['RELAY_BOX_MODBUS_UNIT'] is not None:
            try:
                self.relay_box = modbus_reader.ModbusRelayBoxReader(
                    'rb',
                    unit_id=int(self.configurations['RELAY_BOX_MODBUS_UNIT']),
                    produce_dummy_data=self.configurations['DUMMY_DATA']
                )
            except Exception as e:
                print(e)
                self.relay_box = None
        else:
            self.relay_box = None

        if self.configurations['MCU_ARDUINO_I2C_ADDRESS'] is not None:
            try:
                self.mcu = mcu_arduino_reader.McuArduinoReader(
                    'mcu',
                    produce_dummy_data=self.configurations['DUMMY_DATA']
                )
            except Exception as e:
                print(e)
                self.mcu = None
        else:
            self.mcu = None

    def read_and_publish(self, data):
        try:
            single_values_data = data.stocazzo_format()
            for value in single_values_data:
                self.mqtt_client.publish(IIoT.MqttChannels.sensors, value)
        except Exception as e:
            print(e)

    def read(self):
        # Read the data
        if self.charge_controller is not None:
            try:
                self.read_and_publish(self.charge_controller.read())
            except Exception as e:
                print(e)

        if self.charge_controller_2 is not None:
            try:
                self.read_and_publish(self.charge_controller_2.read())
            except Exception as e:
                print(e)

        if self.relay_box is not None:
            try:
                self.read_and_publish(self.relay_box.read())
            except Exception as e:
                print(e)

        if self.mcu is not None:
            try:
                self.read_and_publish(self.mcu.read())
            except Exception as e:
                print(e)

    def change_property(self, key, value):
        self.configurations[str(key)] = value

        configs = configparser.ConfigParser()
        configs[str(key)] = value

        # save to file
        with open(self.config_file, 'w') as configfile:
            configs.write(configfile)

        # reinitialize the objects
        self.init_sensors()

    def on_configuration_message_callback(self, message):
        message_payload = json.loads(message.payload)
        message_topic = message.topic

        print(message_topic)
        print(message_payload)

        try:
            _, mqtt_channel, device, key, direction = message_topic.split('/')
        except Exception as e:
            print(e)
            return None

        message_payload = json.loads(message.payload)
        value_type = message_payload['value_type']
        value = message_payload['value']

        response_topic = "/{}/{}/{}/response".format(mqtt_channel, device, key)

        try:
            self.change_property(key, value)
        except Exception as e:
            # publish back
            print(e)
        self.mqtt_client.publish(response_topic, message_payload)

    def run(self):
        self.mqtt_client.start()
        while True:
            self.read()
            sleep(self.get_properties()['READING_INTERVAL'])