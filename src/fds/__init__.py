import json

from fds.Boards import C23
from libs.utils import connector, IIoT

if __name__ == "__main__":
    board = None
    topics = [IIoT.MqttChannels.persist, IIoT.MqttChannels.sensors, IIoT.MqttChannels.telemetry]
    mqtt_client = connector.MqttLocalClient('FDS', 'localhost', 1883)
    mqtt_client.run()

    # initialize the MCU object
    try:
        print('Initializing MCU connection...')
        board = C23(debug=True)
    except Exception as e:
        print(e)

    while True:
        data = board.read()
        mqtt_client.publish_on_many_topics(topics, json.dumps(data))
