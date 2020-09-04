import json
from datetime import datetime
from time import sleep

from sensor import modbus_reader
from sensor import mcu_arduino_reader

from libs.utils import connector, IIoT

import os

import configparser


## parametri
MQTT_HOSTNAME  = os.getenv('MQTT_HOSTNAME', 'mosquitto')
MQTT_PORT      = os.getenv('MQTT_PORT', '1883')
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'CHARGE_CONTROLLER_1')

'''
READING_INTERVAL                = int(os.getenv('READING_INTERVAL', 10))
MODBUS_IP                       = os.getenv('MODBUS_IP','192.168.2.253')
CHARGE_CONTROLLER_1_MODBUS_UNIT = os.getenv('CHARGE_CONTROLLER_1_MODBUS_UNIT', None) #0x1
CHARGE_CONTROLLER_2_MODBUS_UNIT = os.getenv('CHARGE_CONTROLLER_2_MODBUS_UNIT', None)
RELAY_BOX_MODBUS_UNIT           = os.getenv('RELAY_BOX_MODBUS_UNIT'          , None) #0x09
MCU_I2C_CHANNEL                 = os.getenv('MCU_I2C_CHANNEL', 1)
MCU_ARDUINO_I2C_ADDRESS         = os.getenv('MCU_ARDUINO_I2C_ADDRESS', None) #0x27

DUMMY_DATA                      = bool(os.getenv('DUMMY_DATA', False))
'''
CONFIG_FILE = 'config.ini'

######## vediamo se fare cosi o no
class Configs():

    def __init__(self):
        self.configurations = None



class Sensors():

    def __init__(self):

        self.configurations = None

        self.charge_controller = None
        self.charge_controller_2 = None
        self.relay_box = None
        self.mcu = None

    def init_properties(self):
        configs = configparser.ConfigParser()
        configs.read( CONFIG_FILE )

        if configs['READING_INTERVAL'] is '':
            self.read_properties_from_env()
        else:
            self.read_properites_from_file()

    def read_properties_from_env(self):
        self.configurations['READING_INTERVAL'] = int( os.getenv('READING_INTERVAL', 10) )
        self.configurations['DUMMY_DATA'] = bool( os.getenv('DUMMY_DATA', False) )
        self.configurations['MODBUS_IP'] = os.getenv('MODBUS_IP','192.168.2.253')
        self.configurations['CHARGE_CONTROLLER_1_MODBUS_UNIT'] = os.getenv('CHARGE_CONTROLLER_1_MODBUS_UNIT', None) #0x1
        self.configurations['CHARGE_CONTROLLER_2_MODBUS_UNIT'] = os.getenv('CHARGE_CONTROLLER_2_MODBUS_UNIT', None)
        self.configurations['RELAY_BOX_MODBUS_UNIT']  = os.getenv('RELAY_BOX_MODBUS_UNIT', None) #0x09
        self.configurations['MCU_I2C_CHANNEL'] = os.getenv('MCU_I2C_CHANNEL', 1)
        self.configurations['MCU_ARDUINO_I2C_ADDRESS'] = os.getenv('MCU_ARDUINO_I2C_ADDRESS', None) #0x27

    def read_properites_from_file(self):
        configs = configparser.ConfigParser()
        configs.read( CONFIG_FILE )
        self.configurations['READING_INTERVAL'] = int( configs['READING_INTERVAL'] )
        self.configurations['MODBUS_IP']  = configs['MODBUS_IP']
        self.configurations['CHARGE_CONTROLLER_1_MODBUS_UNIT'] = configs['CHARGE_CONTROLLER_1_MODBUS_UNIT']
        self.configurations['CHARGE_CONTROLLER_2_MODBUS_UNIT'] = configs['CHARGE_CONTROLLER_2_MODBUS_UNIT']
        self.configurations['RELAY_BOX_MODBUS_UNIT'] = configs['RELAY_BOX_MODBUS_UNIT']
        self.configurations['MCU_I2C_CHANNEL'] = configs['MCU_I2C_CHANNEL']
        self.configurations['MCU_ARDUINO_I2C_ADDRESS'] = configs['MCU_ARDUINO_I2C_ADDRESS']
        self.configurations['DUMMY_DATA'] = bool( configs['DUMMY_DATA'] )


    def get_properties(self):
        return self.configurations

    def init_sensors(self):
        if self.configurations['CHARGE_CONTROLLER_1_MODBUS_UNIT'] is not None:
            try:
                self.charge_controller = modbus_reader.ModbusChargeControllerReader(
                    'cc1',
                    unit_id=int( self.configurations['CHARGE_CONTROLLER_1_MODBUS_UNIT'] ),
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
                    unit_id=int( self.configurations['CHARGE_CONTROLLER_2_MODBUS_UNIT'] ),
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
                mqtt_client.publish(IIoT.MqttChannels.sensors, value )
        except Exception as e:
            print( e )

    def read(self):
        # Read the data
        if self.charge_controller is not None:
            try:
                self.read_and_publish( self.charge_controller.read() )
            except Exception as e:
                print( e )

        if self.charge_controller_2 is not None:
            try:
                self.read_and_publish( self.charge_controller_2.read() )
            except Exception as e:
                print( e )

        if self.relay_box is not None:
            try:
                self.read_and_publish( self.relay_box.read() )
            except Exception as e:
                print( e )

        if self.mcu is not None:
            try:
                self.read_and_publish( self.mcu.read() )
            except Exception as e:
                print( e )


    def change_property(self, key, value):
        self.configurations[str(key)] = value

        configs = configparser.ConfigParser()
        configs[str(key)] = value

        # save to file
        with open(CONFIG_FILE, 'w') as configfile:
            configs.write(configfile)

        # reinitialize the objects
        sensors.init_sensors()



    def on_configuration_message_callback(message):
        message = mqtt_client.message_queue.get()
        message_payload = json.loads(message.payload)
        message_topic = message.topic()

        print(message_topic)
        print(message_payload)

        try:
            mqtt_channel, device, key, direction = message_topic.split('/')
        except Exception as e:
            print(e)
            return None

        message_payload = json.loads(message.payload)
        value_type = message_payload['value_type']
        value      = message_payload['value']

        response_topic = mqtt_channel + "/" + device + "/" + key + "/response"

        try:
            sensors.change_property(response_topic, key, value)
        except Exception as e:
            # publish back
            mqtt_client.publish(response_topic, value)


if __name__ == "__main__":

    sensors = Sensors()
    sensors.init_properties()
    sensors.init_sensors()

    topics = ["/configurations"]
    mqtt_client = connector.MqttLocalClient(MQTT_CLIENT_ID, MQTT_HOSTNAME, int(MQTT_PORT), topics)
    mqtt_client.setCallback( sensors.on_configuration_message_callback() )
    mqtt_client.start()

    topics_tables_mapper = {
        IIoT.MqttChannels.sensors: 'sensors',
    }



    while True:
        sensors.read()
        sleep( sensors.get_properties()['READING_INTERVAL'] )
