import json
from abc import abstractmethod, ABC
from datetime import datetime
from random import randrange



class Reader(ABC):

    @abstractmethod
    def read(self) -> SensorValue:
        pass


########################

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



class DummyReader(Reader):

    def __init__(self, key):
        self.key = key

    def read(self) -> SensorValue:
        return SensorValue(self.key, randrange(10, 100), int(datetime.now().timestamp()))

########################

class ModbusSensorValue:

    def __init__(self, key, value, timestamp):
        self.key       = key
        self.value     = value
        self.timestamp = timestamp

    def format(self):
        return json.dumps({
            "key":       self.key,
            "value":     self.value,
            "timestamp": self.timestamp
        })


# Modbus reader
class ModbusReader(Reader):

    def __init__(self, key, port = DEFAULT_PORT, baudrate = DEFAULT_BAUDRATE, produce_dummy_data = False):
        self.key = key
        self.port = port
        self.baudrate = baudrate
        self.produce_dummy_data = produce_dummy_data


    def read(self) -> SensorValue:
        data = getData()
        return SensorValue(self.key, data, int(datetime.now().timestamp()))


    def connect(self):
        try:
            print("Connect modbus...")
            self.client = ModbusClient(method='rtu', port=self.port, baudrate=self.baudrate)
            self.client.connect()
        except Exception as e:
            err = 'Error in Modbus Connect: ' + str(e)
            print( err )


    def disconnect(self):
        try:
            self.client.diconnect()
        except Exception as e:
            err = 'Error in Modbus Disconnect: ' + str(e)
            print( err )


    def readRegisters(self):
        try:
            result = client.read_input_registers(0x3100, 15, unit=1)
        except Exception as e:
            result = None
            err = 'Error in Modbus reading registers: ' + str(e)
            print( err )

        return result


    def getData(self):
        result = readRegisters()

        if registers == None:
            return None

        data = dict()

        try:
            data['panelVoltage']   = float( result.registers[0]  / 100.0 )
            data['panelCurrent']   = float( result.registers[1]  / 100.0 )
            data['batteryVoltage'] = float( result.registers[4]  / 100.0 )
            data['batteryCurrent'] = float( result.registers[5]  / 100.0 )
            data['loadVoltage']    = float( result.registers[12] / 100.0 )
            data['loadCurrent']    = float( result.registers[13] / 100.0 )
        except Exception as e:
            data = None
            err = 'Error parsing Modbus readings: ' + str(e)
            print( err )

        return data
