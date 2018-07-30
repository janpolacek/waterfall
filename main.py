import RPi.GPIO as GPIO           # import RPi.GPIO module
from mcp3208 import MCP3208
import time

PUMP_PIN = 4
SENSOR_CHANNEL = 0

MIN_SOIL_VALUE = 1800   #Hodnota vo vode
MAX_SOIL_VALUE = 4095   #Hodnota kedy je uplne sucho
WATER_PER_PLANT = 0.3    #Liter
WATER_PUMP_POWER = 120  #Litrov za hodinu
WATERING_TIME = WATER_PER_PLANT * 3600 / WATER_PUMP_POWER
WATCH_FREQUENCY = 4*3600 #Raz za 4 hodiny
MIN_SOIL_MOISTURE_LEVEL = 40

adc = MCP3208()

def moisture_percentage(v):
    return 100 - ((v - MIN_SOIL_VALUE )/ (MAX_SOIL_VALUE - MIN_SOIL_VALUE) * 100)


GPIO.setmode(GPIO.BCM)             # choose BCM or BOARD
GPIO.setup(PUMP_PIN, GPIO.OUT)           # set GPIO4 as an output
try:
    while True:
        moisture_val = adc.read(SENSOR_CHANNEL)
        print('Moisture value', moisture_val)
        moisture_level =  moisture_percentage(moisture_val)
        print('Moisture level: {:.2f} %'.format(moisture_level))

        if moisture_level < MIN_SOIL_MOISTURE_LEVEL:
            GPIO.output(PUMP_PIN, GPIO.LOW)  # set GPIO4 to 1/GPIO.HIGH/True
            print('Pump turned ON')
            time.sleep(WATERING_TIME)

        GPIO.output(PUMP_PIN, GPIO.HIGH)  # set GPIO4 to 1/GPIO.HIGH/True
        print('Pump turned OFF')
        time.sleep(WATCH_FREQUENCY)
        print('\n')


except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
    GPIO.cleanup()

