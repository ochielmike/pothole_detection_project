import RPi.GPIO as GPIO
import serial
import time

class SIM7600X:
    def __init__(self, tty, baudrate, power_key):
        self.ser = serial.Serial(tty, baudrate)
        self.ser.flushInput()
        self.power_key = power_key
        self.rec_buff = ''
        self.rec_buff2 = ''
        self.time_count = 0

    def send_at(self, command, back, timeout):
        c =0
        self.rec_buff = ''
        self.ser.write((command+'\r\n').encode())
        time.sleep(timeout)
        if self.ser.inWaiting():
            time.sleep(0.01)
            self.rec_buff = self.ser.read(self.ser.inWaiting())
        if self.rec_buff != '':
            if back not in self.rec_buff.decode():
                print(command + ' ERROR')
                print(command + ' back:\t' + self.rec_buff.decode())
                return 0
            else:
                c+=1
                out= self.rec_buff.decode()
                #print(self.rec_buff.decode())
                
                print('int c'+ str(c))
                #lis_out=[1, out]
                #print(list_out)
                print(out)
                return 1,out
        else:
            print('GPS is not ready')
            return 0

    def get_gps_position(self):
        rec_null = True
        answer = 0
        print('Retreiving GPS info...')
        self.rec_buff = ''
        #self.send_at('AT+CGPS=1,1','OK',1)
        #time.sleep(2)
        a =0
        b =0
        while rec_null:
            answer,SIM_out = self.send_at('AT+CGPSINFO','+CGPSINFO: ',1)
            if 1 == answer:
                print(answer)
                answer = 0
                if ',,,,,,,,' in SIM_out:
                    a=a+1
                    print('int a'+ str(a))
                    print('GPS info unavailable')
                    #answer,SIM_out = self.send_at('AT+CGPSINFO','+CGPSINFO: ',1)
                    if a>20 and ',,,,,,,,' in SIM_out:
                        rec_null = False
                    time.sleep(1)
                else:
                    #print('error %d'%answer)
                    print('int b'+ str(b))
                    output_redacted = SIM_out[13:]
                    print("output_redacted:",output_redacted)
                    output_l = output_redacted.split(',')
                    print("Output list:", output_l)
                    if len(output_l) < 4:
                        return None
                    lat = output_l[0]
                    lat_direction = output_l[1]
                    lon = output_l[2]
                    lon_direction = output_l[3]
                    date_d = output_l[4]
                    time_t = output_l[5]
                    lat_l = lat.split('.')
                    lon_l = lon.split('.')
                    lat_degrees = int(lat_l[0][:-2])
                    lon_degrees = int(lon_l[0][:-2])
                    lat_minutes = float(lat[len(str(lat_degrees)):]) / 60
                    lon_minutes = float(lon[len(str(lon_degrees)):]) / 60
                    lat_out = lat_degrees + lat_minutes
                    lon_out = lon_degrees + lon_minutes
                    if lat_direction == 'S':
                        lat_out = -lat_out
                    if lon_direction == 'W':
                        lon_out = -lon_out
                    
                    self.rec_buff = ''
                    
                    #self.send_at('AT+CGPS=0','OK',1)
                    #return False
                    return lat_out, lon_out, date_d, time_t
    
                    
            time.sleep(1.5)

    def power_on(self):
        print('SIM7600X is starting:')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.power_key, GPIO.OUT)
        time.sleep(0.1)
        GPIO.output(self.power_key, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(self.power_key, GPIO.LOW)
        time.sleep(20)
        self.ser.flushInput()
        print('SIM7600X is ready')
        
        rec_null = True
        answer = 0
        print('Start GPS session...')
        self.rec_buff = ''
        self.send_at('AT+CGPS=1,1','OK',1)
        time.sleep(2)
        a =0
        b =0
        while rec_null:
            answer,SIM_out = self.send_at('AT+CGPSINFO','+CGPSINFO: ',1)
            if 1 == answer:
                print(answer)
                answer = 0
                if ',,,,,,,,' in SIM_out:
                    a=a+1
                    print('int a'+ str(a))
                    print('GPS is not ready')
                    #answer,SIM_out = self.send_at('AT+CGPSINFO','+CGPSINFO: ',1)
                    if a>1000 and ',,,,,,,,' in SIM_out:
                        rec_null = False
                    time.sleep(1)
                else:
                    #print('error %d'%answer)
                    print('GPS is ready')
                    rec_null = False

    def power_down(self):
        print('SIM7600X is logging off:')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.power_key, GPIO.OUT)
        time.sleep(0.1)
        GPIO.output(self.power_key, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(self.power_key, GPIO.LOW)
        time.sleep(18)
        print('Good bye')
