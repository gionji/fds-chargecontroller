import configparser
import json
import os
import threading

from . import modbus_reader, mcu_arduino_reader
from ..utils import IIoT
from ..utils.connector import MqttLocalClient


class Sensors(threading.Thread):

    def __init__(self, config_file, mqtt_client: MqttLocalClient):
        super().__init__()

        self.configurations = {}
        self.charge_controller = None
        self.charge_controller_2 = None
        self.relay_box = None
        self.mcu = None
        self.event = threading.Event()

        self.mqtt_client = mqtt_client
        self.config_file = config_file

        self.mqtt_client.set_callback(self.on_message_callback)

    def init_properties(self):

        if self.config_file is None:
            self.read_properties_from_env()
        else:
            self.read_properties()

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

    def read_properties(self):
        configs = configparser.ConfigParser()
        configs.read(self.config_file)

        default = configs['DEFAULT']
        self.configurations['READING_INTERVAL'] = int(default['READING_INTERVAL'.lower()])
        self.configurations['MODBUS_IP'] = default['MODBUS_IP'.lower()]
        self.configurations['CHARGE_CONTROLLER_1_MODBUS_UNIT'] = default['CHARGE_CONTROLLER_1_MODBUS_UNIT'.lower()]
        self.configurations['CHARGE_CONTROLLER_2_MODBUS_UNIT'] = default['CHARGE_CONTROLLER_2_MODBUS_UNIT'.lower()]
        self.configurations['RELAY_BOX_MODBUS_UNIT'] = default['RELAY_BOX_MODBUS_UNIT'.lower()]
        self.configurations['MCU_I2C_CHANNEL'] = default['MCU_I2C_CHANNEL'.lower()]
        self.configurations['MCU_ARDUINO_I2C_ADDRESS'] = default['MCU_ARDUINO_I2C_ADDRESS'.lower()]
        self.configurations['DUMMY_DATA'] = bool(int(default['DUMMY_DATA'.lower()]))

    def get_properties(self):
        return self.configurations

    def init_sensors(self):
        self.read_properties()
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
        single_values_data = data.stocazzo_format()
        for value in single_values_data:
            topic = '{}/{}/{}'.format(IIoT.MqttChannels.sensors, self.mqtt_client.client_id, value['sensor'])
            self.mqtt_client.publish(topic, json.dumps(value))

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

    def change_property(self, key, value, value_type):
        self.configurations[str(key)] = value

        # TODO: cast in base a value_type

        configs = configparser.ConfigParser()
        configs.read(self.config_file)
        configs['DEFAULT'][key] = value

        # save to file
        with open(self.config_file, 'w') as configfile:
            configs.write(configfile)

        # reinitialize the objects
        self.init_properties()
        self.init_sensors()

    def on_message_callback(self, message):
        message_payload = json.loads(message.payload)
        message_topic = message.topic

        print(message_topic)
        print(message_payload)

        try:
            _, mqtt_channel, module, configuration, direction = message_topic.split('/')
        except Exception as e:
            print(e)
            return None

        message_payload = json.loads(message.payload)
        value_type = message_payload['value_type']
        value = message_payload['value']

        if mqtt_channel == 'configurations':
            try:
                self.change_property(configuration, value, value_type)
            except Exception as e:
                # publish back
                print(e)
        elif mqtt_channel == 'actuators':
            print(message_payload)

        response_topic = "/{}/{}/{}/response".format(mqtt_channel, module, configuration)
        self.mqtt_client.publish(response_topic, json.dumps(message_payload))

    def start(self):
        self.mqtt_client.start()
        while True:
            self.read()
            self.event.wait(self.get_properties()['READING_INTERVAL'])

    def stop(self):
        self.event.set()
        self.mqtt_client.stop()
        self.mqtt_client.join()
        self.join()
