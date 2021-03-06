import json
from abc import abstractmethod, ABC
from datetime import datetime
from random import randrange


class SensorValue:

    def __init__(self, key, value, timestamp):
        self.key = key
        self.value = value
        self.timestamp = timestamp

    def format(self):
        return json.dumps({
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp
        })

    def pretty_format(self):
        return json.dumps({
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp},
            sort_keys=True,
            indent=4
        )

    def stocazzo_format(self):
        values = list()
        device_type = self.value['type']

        for key, value in self.value.items():
            if key != 'type':

                value_type = str(type(value)).split("'")[1]

                if value_type == 'str':
                    value_type = 'string'

                value_obj = {
                    "sensor": '{}_{}'.format(device_type, key),
                    "value_type": value_type,
                    "value": value,
                    "timestamp": self.timestamp
                }
                values.append(value_obj)

        return values


class Reader(ABC):

    @abstractmethod
    def read(self) -> SensorValue:
        pass


class DummyReader(Reader):

    def __init__(self, key):
        self.key = key

    def read(self) -> SensorValue:
        return SensorValue(self.key, randrange(10, 100), int(datetime.now().timestamp()))
