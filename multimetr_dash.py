#!/usr/bin/python

import serial
import matplotlib.pyplot as plt
import time
from matplotlib.animation import FuncAnimation
import matplotlib.ticker as ticker
from statistics import mean


class HP34401A:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=10):
        self.ser = serial.Serial(
            port=port, baudrate=baudrate, timeout=timeout, stopbits=serial.STOPBITS_TWO)

    def send_command(self, command, asyn=True):
        self.ser.write(command.encode() + b'\r\n')
        return "" if asyn else self.ser.readline().decode().strip()

    def reset(self):
        self.ser.write('*RST\r\n'.encode())
        self.ser.write('*CLS\r\n'.encode())
        time.sleep(0.5)

    def remote(self):
        self.ser.write('SYST:REM\r\n'.encode())
        time.sleep(0.5)

    def set_voltage_dc_mode(self, range='DEF', resolution=0.001):
        # self.reset()
        self.send_command('CONF:VOLT:DC')
        # self.send_command('VOLT:DC:RANGE ' + str(range))
        # self.send_command(':VOLT:DC:RES? ' + str(resolution))
        # self.send_command('MEAS:VOLT:DC? ' +  str(range) + str(",") + str(resolution))
        self.send_command(':VOLT:DC:NPLC ' + str(0.2))

    def set_current_dc_mode(self, range='AUTO', resolution=0.00001):
        self.send_command(':MEAS:CURR:DC')
        self.send_command(':MEAS:CURR:DC:RANGE ' + str(range))
        self.send_command(':MEAS:CURR:DC:RES ' + str(resolution))

    def set_resistance_mode(self, range='AUTO', resolution=0.01):
        self.send_command(':MEAS:RES')
        self.send_command(':MEAS:RES:RANGE ' + str(range))
        self.send_command(':MEAS:RES:RES ' + str(resolution))

    def set_frequency_mode(self, range='AUTO', resolution=0.001):
        self.send_command(':MEAS:FREQ')
        self.send_command(':MEAS:FREQ:RANGE ' + str(range))
        self.send_command(':MEAS:FREQ:RES ' + str(resolution))

    def set_period_mode(self, range='AUTO', resolution=0.001):
        self.send_command(':MEAS:PER')
        self.send_command(':MEAS:PER:RANGE ' + str(range))
        self.send_command(':MEAS:PER:RES ' + str(resolution))

    def read_value(self):
        return self.send_command(':READ?', asyn=False)


class MultimeterData:
    def __init__(self, multimeter: HP34401A, duration):
        self.multimeter = multimeter
        # self.duration = duration
        self.data = {'time': [], 'voltage': []}

        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Real-time voltage measurement")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Voltage (V)")

    def start(self):
        print("Auto DC Volts measuring", self.multimeter.set_voltage_dc_mode())
        self.ani = FuncAnimation(
            self.fig, self.update, interval=0, blit=False, cache_frame_data=False)
        plt.show(block=True)
        exit(0)

    def update(self, frame):
        value = self.multimeter.read_value()
        if "" == value:
            print("Read Error!")
            self.multimeter.reset()
            return
        voltage = float(value)
        print("value:", voltage)
        current_time = time.time()
        self.data['time'].append(current_time)
        self.data['voltage'].append(voltage)
        if self.data["time"].__len__() > 500:
            self.data["time"].pop(0)
            self.data["voltage"].pop(0)

        self.plot_data()

    def plot_data(self):
        self.ax.clear()
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Voltage (V)")
        self.ax.plot(self.data["time"], self.data["voltage"])
        self.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%f'))

        self.ax.plot(self.data["time"][-1], self.data["voltage"][-1], "ro")
        # text = f'{(self.data["voltage"][-1]):.9f} volt  '
        # self.ax.text(self.data["time"][-1], self.data["voltage"][-1], text, ha='right', va='bottom', fontsize=15)

        avg_volts = mean(self.data["voltage"])
        text = f'Current: {(self.data["voltage"][-1]):.9f}v;  Mean: {(avg_volts):.9f}v'
        # self.ax.text(self.data["time"][-1], self.ax.get_ybound()[1]-(self.ax.get_ybound()[
        #              1]-self.ax.get_ybound()[0])*0.03, text, ha='right', va='top', fontsize=12)
        self.ax.set_title(text)

        self.fig.canvas.draw()


multimeter = HP34401A(
    '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_CJDEb116L16-if00-port0')
data = MultimeterData(multimeter, 10)

while True:
    multimeter.reset()
    multimeter.remote()
    multimeter.set_voltage_dc_mode()
    data.start()

exit(0)
