import os
import sys

from app.sensor.sensors import Sensors
from app.utils import connector, IIoT

CONFIG_FILE = 'config.ini'

MQTT_HOSTNAME = os.getenv('MQTT_HOSTNAME', 'mosquitto')
MQTT_PORT = os.getenv('MQTT_PORT', '1883')
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'CHARGE_CONTROLLER')


def run(config):
    if not os.path.exists(config):
        exit(1)
    abs_path = os.path.abspath(config)

    print(abs_path)

    topics = [
        '{}/{}/+/request'.format(IIoT.MqttChannels.configurations, MQTT_CLIENT_ID),
        '{}/{}/+/request'.format(IIoT.MqttChannels.actuators, MQTT_CLIENT_ID)
    ]
    mqtt_client = connector.MqttLocalClient(MQTT_CLIENT_ID, MQTT_HOSTNAME, int(MQTT_PORT), topics)
    sensors = Sensors(abs_path, mqtt_client)
    sensors.init_properties()
    sensors.init_sensors()
    mqtt_client.set_callback(sensors.on_configuration_message_callback)
    sensors.run()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = CONFIG_FILE
    run(config_file)
