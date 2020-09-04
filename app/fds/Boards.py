from abc import abstractmethod, ABC
import time

from .FdsSensorUnico import FdsSensor


class Board(ABC):
    IS_MCU_IN_DEBUG_MODE = 1
    BUS_I2C = 1
    MCU_MAX_ATTEMPTS = 10
    RESET_PIN = 10

    sensor = None

    def __init__(self, debug=False):
        self.sensor = FdsSensor(debug=debug, bus_id=self.BUS_I2C)

    @abstractmethod
    def reset_mcu(self):
        pass

    def read(self):
        mcu_data = dict()

        # get Data from MCUs
        for attempt in range(0, self.MCU_MAX_ATTEMPTS):
            # initialize the data structure for MCU da
            mcu_data.clear()
            try:
                mcu_data = self.sensor.get_mcu_data()
                print("I2C read attempt " + str(attempt) + ": ok")
                break
            except Exception as e:
                mcu_data = None
                print("I2C read attempt " + str(attempt) + ": FAIL  " + str(e))

        # if after all the cycles the mcu is stuck try reset
        if mcu_data is None:
            print("MCU RESET: MCU i2c probably stuck!")
            self.reset_mcu()

        return mcu_data


class C23(Board):
    BOARD_TYPE = "C23"
    BUS_I2C = 1
    reset_pin = 149

    def __init__(self, debug=False, reset_pin=None):
        super().__init__(debug)
        if reset_pin is not None:
            self.reset_pin = reset_pin

    def reset_mcu(self):
        try:
            with open("/sys/class/pwm/pwmchip4/export", "w") as pwm:
                pwm.write("0")
        except Exception as e:
            print(e)

        try:
            with open("/sys/class/pwm/pwmchip4/pwm0/period", "w") as pwm:
                pwm.write("100")
        except Exception as e:
            print(e)

        try:
            with open("/sys/class/pwm/pwmchip4/pwm0/duty_cycle", "w") as pwm:
                pwm.write("100")
        except Exception as e:
            print(e)

        try:
            with open("/sys/class/pwm/pwmchip4/pwm0/enable", "w") as pwm:
                pwm.write("0")
                pwm.flush()
                time.sleep(1.0)
                pwm.write("1")
                pwm.flush()
        except Exception as e:
            print(e)


class NEO(Board):
    BOARD_TYPE = "NEO"
    BUS_I2C = 1
    reset_pin = 39

    def __init__(self, debug=False, reset_pin=None):
        super().__init__(debug)
        if reset_pin is not None:
            self.reset_pin = reset_pin

    def reset_mcu(self):
        gpios = [
            "178", "179", "104", "143", "142", "141", "140", "149", "105", "148",
            "146", "147", "100", "102", "102", "106", "106", "107", "180", "181",
            "172", "173", "182", "124", "25", "22", "14", "15", "16", "17",
            "18", "19", "20", "21", "203", "202", "177", "176", "175", "174",
            "119", "124", "127", "116", "7", "6", "5", "4"]

        gpio = gpios[self.reset_pin]

        try:
            with open("/sys/class/gpio/gpio" + gpio + "/direction", "w") as re:
                re.write("out")
            with open("/sys/class/gpio/gpio" + gpio + "/value", "w") as writes:
                writes.write("0")
                time.sleep(1.0)
                writes.write("1")
                time.sleep(1.0)
        except Exception as e:
            print(e)
