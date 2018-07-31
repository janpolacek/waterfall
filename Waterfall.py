import sys
import RPi.GPIO as GPIO
from mcp3208 import MCP3208
import time
from time import gmtime, strftime


class Waterfall:
    PUMP_PIN = 4
    SENSOR_CHANNEL = 0

    MIN_SOIL_VALUE = 1300  # Hodnota vo vode
    MAX_SOIL_VALUE = 4095  # Hodnota kedy je uplne sucho
    WATER_PER_PLANT = 0.3  # Liter
    WATER_PUMP_POWER = 120  # Litrov za hodinu
    WATERING_TIME = WATER_PER_PLANT * 3600 / WATER_PUMP_POWER
    # WATCH_FREQUENCY = 4*3600 #Raz za 4 hodiny
    WATCH_FREQUENCY = 15  # Raz za 15s
    MIN_SOIL_MOISTURE_LEVEL = 40 # Hodnota
    MAX_SOIL_MOISTURE_LEVEL = 80 # Hodnota kedy sa vypne cerpadlo

    FREQUENCY_CHECK = 10 # Hz

    def __init__(self):
        print(self.read_logo())
        self.adc = MCP3208()
        GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
        GPIO.setup(self.PUMP_PIN, GPIO.OUT)

    @staticmethod
    def read_logo():
        with open('logo.txt', 'r') as myfile:
            return myfile.read()


    def calculate_level(self, v):
        return 100 - ((v - self.MIN_SOIL_VALUE) / (self.MAX_SOIL_VALUE - self.MIN_SOIL_VALUE) * 100)

    def read_sensor_values(self):
        moisture_val = self.adc.read(self.SENSOR_CHANNEL)
        moisture_level = self.calculate_level(moisture_val)
        return [moisture_val, moisture_level]

    def turn_pump_on(self):
        GPIO.output(self.PUMP_PIN, GPIO.LOW)

    def turn_pump_off(self):
        GPIO.output(self.PUMP_PIN, GPIO.HIGH)

    def start(self):
        try:
            while True:
                self.run_procedure()
        except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
            GPIO.cleanup()

    def run_procedure(self):
        print('Time:', strftime("%d.%m.%Y %H:%M:%S", gmtime()))
        moisture_val, moisture_level = self.read_sensor_values()
        print('Moisture level: {:.2f}% ({:.2f})'.format(moisture_level, moisture_val))

        if moisture_level < self.MIN_SOIL_MOISTURE_LEVEL:
            self.turn_pump_on()
            print('Water pump turned on')
            try:
                for i in range(int(self.WATERING_TIME) * self.FREQUENCY_CHECK, 0, -1):
                    moisture_val, moisture_level = self.read_sensor_values()
                    sys.stdout.write('Watering time remaining {:.2f}s, moisture level: {:.2f}% ({:.2f})\r'.format( (i-1)/self.FREQUENCY_CHECK, moisture_level, moisture_val))
                    time.sleep(1/self.FREQUENCY_CHECK)
                    if moisture_level > self.MAX_SOIL_MOISTURE_LEVEL:
                        raise Exception('\nThreshold level reached')

                print('\nWater pump turned off')

            except Exception as e:
                print(str(e))
                print('Water pump turned off')




        self.turn_pump_off()
        print('\n')
        time.sleep(self.WATCH_FREQUENCY)