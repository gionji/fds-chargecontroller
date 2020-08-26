import json
from datetime import datetime
from time import sleep

from sensor import reader
from libs.utils import connector, IIoT

import os


## parametri
DEFAULT_READING_INTERVAL = 10
DEFAULT_MODBUS_IP        = '192.168.2.253'
DEFAULT_MODBUS_UNIT      = 1
DEFAULT_DUMMY_DATA       = True

READING_INTERVAL = os.getenv('READING_INTERVAL', DEFAULT_READING_INTERVAL)
MODBUS_IP   = os.getenv('DEFAULT_MODBUS_IP', DEFAULT_MODBUS_IP)
MODBUS_UNIT = os.getenv('DEFAULT_MODBUS_UNIT', DEFAULT_MODBUS_UNIT)
DUMMY_DATA  = os.getenv('DEFAULT_DUMMY_DATA', DEFAULT_DUMMY_DATA)

## da variabili ambiente

if __name__ == "__main__":
    topics = [IIoT.MqttChannels.sensors]  # canali a cui mi sottoscrivo
    mqtt_client = connector.MqttLocalClient('SENSORS', 'localhost', 1883, topics)
    mqtt_client.start()

    topics_tables_mapper = {
        IIoT.MqttChannels.sensors: 'sensors',
    }

    charge_controller = reader.ModbusChargeControllerReader( 'cc1',
                                             produce_dummy_data = True)



    charge_controller_2 = reader.ModbusChargeControllerReader( 'cc2',
                                             produce_dummy_data = True)



    relay_box = reader.ModbusRelayBoxReader( 'rb',
                                             produce_dummy_data = True)

    while True:
        # Read the data
        # charge_controller.connect()
        data1 = charge_controller.read()
        data2 = charge_controller_2.read()
        data3 = relay_box.read()
        #charge_controller.disconnect()

        print(data1.pretty_format())
        print(data2.pretty_format())
        print(data3.pretty_format())

        # Publish the data
        #mqtt_client.publish(IIoT.MqttChannels.sensors, readed_value.format() )

        sleep(READING_INTERVAL)
