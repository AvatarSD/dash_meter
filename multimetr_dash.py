import serial

class h034401a_t:
    def __init__(self, port):
        self.ser = serial.Serial(port, baudrate=9600, timeout=1)
        self.set_rem()
    
    def set_rem(self):
        self.ser.write(b'SYST:REM\n')
        
    def set_dc(self):
        # Відправлення SCPI команди на мультиметр
        self.ser.write(b':CONF:VOLT:DC\n')

        # Зчитування відповіді мультиметра
        return self.ser.readline().decode('utf-8')

    def value(self):
        # Відправлення SCPI команди на мультиметр
        self.ser.write(b':READ?\n')

        # Зчитування відповіді мультиметра
        response = self.ser.readline().decode('utf-8')
        return float(response.strip())

# Використання класу
multimeter = h034401a_t('/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_CJDEb116L16-if00-port0')
print("Switch to DC Auto 7digit", multimeter.set_dc())
while True:
    print('Voltage:', multimeter.value());
