import os
import sys

from app.sensor.sensors import Sensors
from app.utils import connector, IIoT

MQTT_HOSTNAME = os.getenv('MQTT_HOSTNAME', 'localhost')
MQTT_PORT = os.getenv('MQTT_PORT', '1883')
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'CHARGE_CONTROLLER')


def run(config):
    if config is not None:
        if os.path.exists(config):
            config = os.path.abspath(config)
        else:
            exit(1)
    else:
        if os.path.exists('./config.ini'):
            config = os.path.abspath('./config.ini')
        else:
            config = None

    print(config)

    topics = [
        '{}/{}/+/request'.format(IIoT.MqttChannels.configurations, MQTT_CLIENT_ID),
        '{}/{}/+/request'.format(IIoT.MqttChannels.actuators, MQTT_CLIENT_ID)
    ]
    mqtt_client = connector.MqttLocalClient(MQTT_CLIENT_ID, MQTT_HOSTNAME, int(MQTT_PORT), topics)
    sensors = Sensors(config, mqtt_client)
    sensors.init_properties()
    sensors.init_sensors()
    sensors.daemon = True
    try:
        sensors.start()
    except Exception as e:
        print(e)
        sensors.stop()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = None

    run(config_file)
