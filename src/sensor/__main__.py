import json
from datetime import datetime
from time import sleep

from sensor import modbus_reader
from sensor import mcu_arduino_reader

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

    charge_controller = modbus_reader.ModbusChargeControllerReader( 'cc1',
                                             unit_id = 0x02,
                                             produce_dummy_data = True)



    charge_controller_2 = modbus_reader.ModbusChargeControllerReader( 'cc2',
                                             unit_id = 0x01,
                                             produce_dummy_data = True)



    relay_box = modbus_reader.ModbusRelayBoxReader( 'rb',
                                             unit_id = 0x09,
                                             produce_dummy_data = True)


    mcu = mcu_arduino_reader.McuArduinoReader( 'mcu',
                                             produce_dummy_data = True)

    while True:
        # Read the data
        # charge_controller.connect()
        data_cc_1 = charge_controller.read()
        data_cc_2 = charge_controller_2.read()
        data_rb = relay_box.read()
        data_mcu = mcu.read()

        single_values_data_cc_1 = data_cc_1.stocazzo_format()
        single_values_data_cc_2 = data_cc_2.stocazzo_format()
        single_values_data_rb = data_rb.stocazzo_format()
        single_values_data_mcu = data_mcu.stocazzo_format()


        for v in single_values_data_cc_1:
            mqtt_client.publish(IIoT.MqttChannels.sensors, v )

        for v in single_values_data_cc_2:
            mqtt_client.publish(IIoT.MqttChannels.sensors, v )

        for v in single_values_data_rb:
            mqtt_client.publish(IIoT.MqttChannels.sensors, v )

        for v in single_values_data_mcu:
            mqtt_client.publish(IIoT.MqttChannels.sensors, v )


        sleep(READING_INTERVAL)
