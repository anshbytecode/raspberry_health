import max30102
import hrcalc           # For HR & SPO2 calculations
import Adafruit_DHT
import time
import os
import glob
import RPi.GPIO as GPIO

# -----------------------
# SENSOR SETUP
# -----------------------

# MAX30102 Sensor
m = max30102.MAX30102()

# DHT11 Sensor
DHT_PIN = 4  # GPIO pin connected to DHT11

# PIR Motion Sensor
PIR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# -----------------------
# DS18B20 Body Temperature Sensor Setup
# -----------------------
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]  # Auto detect sensor
device_file = device_folder + '/w1_slave'


def read_ds18b20():
    """Reads body temperature from DS18B20 sensor"""
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_ds18b20()

    temp_data = lines[1].find('t=')

    if temp_data != -1:
        temp_string = lines[1][temp_data+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    return None


# -----------------------
# MAIN LOOP
# -----------------------

print("Starting Health Monitoring System...")
time.sleep(2)

while True:
    try:
        # ---- Heart Rate & SPO2 from MAX30102 ----
        red, ir = m.read_sequential()
        hr, spo2 = hrcalc.calc_hr_and_spo2(ir, red)

        # ---- Read DHT11 (Room Temp + Humidity) ----
        humidity, room_temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)

        # ---- Body Temperature ----
        body_temp = read_ds18b20()

        # ---- Motion Detection ----
        motion = GPIO.input(PIR_PIN)

        # -----------------------
        # PRINT OUTPUT
        # -----------------------
        print("=====================================")
        print(f"Heart Rate     : {hr} BPM")
        print(f"SpO2           : {spo2} %")
        print(f"Room Temp      : {room_temp} °C")
        print(f"Humidity       : {humidity} %")
        print(f"Body Temp      : {body_temp} °C")

        if motion:
            print("Motion         : DETECTED")
        else:
            print("Motion         : No movement")

        print("=====================================")

        # Small delay
        time.sleep(2)

    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()
        break
