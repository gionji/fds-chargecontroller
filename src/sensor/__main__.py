import json
from datetime import datetime
from time import sleep

from sensor import modbus_reader
from sensor import mcu_arduino_reader

from libs.utils import connector, IIoT

import os


## parametri
MQTT_HOSTNAME = os.getenv('MQTT_HOSTNAME', 'mosquitto')
MQTT_PORT = os.getenv('MQTT_PORT', '1883')
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'CHARGE_CONTROLLER_1')

READING_INTERVAL                = int(os.getenv('READING_INTERVAL', 10))
MODBUS_IP                       = os.getenv('MODBUS_IP','192.168.2.253')

CHARGE_CONTROLLER_1_MODBUS_UNIT = os.getenv('CHARGE_CONTROLLER_1_MODBUS_UNIT', None) #0x1
CHARGE_CONTROLLER_2_MODBUS_UNIT = os.getenv('CHARGE_CONTROLLER_2_MODBUS_UNIT', None)
RELAY_BOX_MODBUS_UNIT           = os.getenv('RELAY_BOX_MODBUS_UNIT'          , None) #0x09

MCU_I2C_CHANNEL                 = os.getenv('MCU_I2C_CHANNEL', 1)
MCU_ARDUINO_I2C_ADDRESS         = os.getenv('MCU_ARDUINO_I2C_ADDRESS', None) #0x27

DUMMY_DATA                      = bool(os.getenv('DUMMY_DATA', False))


def read_and_publish(data):
    try:
        single_values_data = data.stocazzo_format()
        for v in single_values_data:
            mqtt_client.publish(IIoT.MqttChannels.sensors, v )
    except Exception as e:
        print( e )

if __name__ == "__main__":
    topics = [IIoT.MqttChannels.sensors]  # canali a cui mi sottoscrivo
    mqtt_client = connector.MqttLocalClient(MQTT_CLIENT_ID, MQTT_HOSTNAME, int(MQTT_PORT), topics)
    mqtt_client.start()

    topics_tables_mapper = {
        IIoT.MqttChannels.sensors: 'sensors',
    }


    if CHARGE_CONTROLLER_1_MODBUS_UNIT != None:
        try:
            charge_controller = modbus_reader.ModbusChargeControllerReader( 'cc1',
                                             unit_id = int(CHARGE_CONTROLLER_1_MODBUS_UNIT),
                                             produce_dummy_data = DUMMY_DATA)
        except Exception as e:
            print( e )


    if CHARGE_CONTROLLER_2_MODBUS_UNIT != None:
        try:
            charge_controller_2 = modbus_reader.ModbusChargeControllerReader( 'cc2',
                                            unit_id = int(CHARGE_CONTROLLER_2_MODBUS_UNIT),
                                            produce_dummy_data = DUMMY_DATA)
        except Exception as e:
           print( e )


    if RELAY_BOX_MODBUS_UNIT != None:
        try:
            relay_box = modbus_reader.ModbusRelayBoxReader( 'rb',
                                                 unit_id = int(RELAY_BOX_MODBUS_UNIT),
                                                 produce_dummy_data = DUMMY_DATA)
        except Exception as e:
            print( e )


    if MCU_ARDUINO_I2C_ADDRESS != None:
        try:
            mcu = mcu_arduino_reader.McuArduinoReader( 'mcu',
                                                 produce_dummy_data = DUMMY_DATA)
        except Exception as e:
            print( e )


    while True:

        # Read the data
        if CHARGE_CONTROLLER_1_MODBUS_UNIT != None:
            read_and_publish(charge_controller.read())
        if CHARGE_CONTROLLER_2_MODBUS_UNIT != None:
            read_and_publish(charge_controller_2.read())
        if RELAY_BOX_MODBUS_UNIT != None:
            read_and_publish(relay_box.read())
        if MCU_ARDUINO_I2C_ADDRESS != None:
            read_and_publish(mcu.read())

        sleep(READING_INTERVAL)
