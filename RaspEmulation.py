# example - 14
# Sending SMS by press a button 
# Developer :ees
# www.eestechcenter.com
#-----------------------------------------------
#hardware conncections

 #LCD-----------Rpi
 #RS------------GPIO 20
 #EN------------GPIO 21
 #D4------------GPIO 6
 #D5------------GPIO 13
 #D6------------GPIO 19
 #D7------------GPIO 26

  # Rpi--------- GSM modem  
  # Tx --------- RX
  # RX --------- TX
  # GPIO 4 ------ Button

#import RPi.GPIO as GPIO
import time
import serial
import time
import sys
from time import sleep

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders


import os
from decimal import *

'''
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(button,GPIO.IN) 

# set up the SPI interface pins

GPIO.setup(GSM_SERIAL, GPIO.OUT)
GPIO.setup(ARDUNO_SERIAL,  GPIO.OUT)

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

'''
button = 4
GSM_SERIAL  = 10
ARDUNO_SERIAL = 9

sensor_Data = []
#-------------------------------------------------

                 
THREEPLACES = Decimal(10) ** -3


#Predefine dictonary for emergency Dial list
emergency_Dial = {'doctor1': '8686618977', 'doctor2': '7036431896', 'hospital': '12345678', 'Relatives': '8686608733'}
#Predefine emailId for emergency mail
emailId = '2017he12520@wilp.bits-pilani.ac.in'

#-----------------------------------------------------------------

def send_mail(toaddr, text):
    
    fromaddr = "patientName@gmail.com"
    #toaddr = "2017he12520@wilp.bitspilani.ac.in"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Alert Message from Health Monitor device!!!"
    body = "Alert Message :" + text + "    " + " Check immediately Thank you"
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "mtechelegant@123")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    print("Mail sent")
    server.quit()
    return

class Adafruit_CharLCD(object):

    # commands
    LCD_CLEARDISPLAY        = 0x01
    LCD_RETURNHOME          = 0x02
    LCD_ENTRYMODESET        = 0x04
    LCD_DISPLAYCONTROL      = 0x08
    LCD_CURSORSHIFT         = 0x10
    LCD_FUNCTIONSET         = 0x20
    LCD_SETCGRAMADDR        = 0x40
    LCD_SETDDRAMADDR        = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT          = 0x00
    LCD_ENTRYLEFT           = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON           = 0x04
    LCD_DISPLAYOFF          = 0x00
    LCD_CURSORON            = 0x02
    LCD_CURSOROFF           = 0x00
    LCD_BLINKON             = 0x01
    LCD_BLINKOFF            = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE         = 0x08
    LCD_CURSORMOVE          = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE         = 0x08
    LCD_CURSORMOVE          = 0x00
    LCD_MOVERIGHT           = 0x04
    LCD_MOVELEFT            = 0x00

    # flags for function set
    LCD_8BITMODE            = 0x10
    LCD_4BITMODE            = 0x00
    LCD_2LINE               = 0x08
    LCD_1LINE               = 0x00
    LCD_5x10DOTS            = 0x04
    LCD_5x8DOTS             = 0x00
    
    def __init__(self, pin_rs=20, pin_e=21, pins_db=[6, 13, 19, 26], GPIO=None):
        # Emulate the old behavior of using RPi.GPIO if we haven't been given
        # an explicit GPIO interface to use
        '''
        if not GPIO:
            import RPi.GPIO as GPIO
            GPIO.setwarnings(False)
        self.GPIO = GPIO
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setup(self.pin_e, GPIO.OUT)
        self.GPIO.setup(self.pin_rs, GPIO.OUT)

        for pin in self.pins_db:
            self.GPIO.setup(pin, GPIO.OUT)
        '''
        self.write4bits(0x33)  # initialization
        self.write4bits(0x32)  # initialization
        self.write4bits(0x28)  # 2 line 5x7 matrix
        self.write4bits(0x0C)  # turn cursor off 0x0E to enable cursor
        self.write4bits(0x06)  # shift cursor right

        self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF

        self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
        self.displayfunction |= self.LCD_2LINE

        # Initialize to default text direction (for romance languages)
        self.displaymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)  # set the entry mode

        self.clear()

    def begin(self, cols, lines):
        if (lines > 1):
            self.numlines = lines
            self.displayfunction |= self.LCD_2LINE

    def home(self):
        self.write4bits(self.LCD_RETURNHOME)  # set cursor position to zero
        self.delayMicroseconds(3000)  # this command takes a long time!

    def clear(self):
        self.write4bits(self.LCD_CLEARDISPLAY)  # command to clear display
        self.delayMicroseconds(3000)  # 3000 microsecond sleep, clearing the display takes a long time

    def setCursor(self, col, row):
        self.row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self.numlines:
            row = self.numlines - 1  # we count rows starting w/0
        self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def noDisplay(self):
        """ Turn the display off (quickly) """
        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def display(self):
        """ Turn the display on (quickly) """
        self.displaycontrol |= self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noCursor(self):
        """ Turns the underline cursor off """
        self.displaycontrol &= ~self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def cursor(self):
        """ Turns the underline cursor on """
        self.displaycontrol |= self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noBlink(self):
        """ Turn the blinking cursor off """
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def blink(self):
        """ Turn the blinking cursor on """
        self.displaycontrol |= self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def DisplayLeft(self):
        """ These commands scroll the display without changing the RAM """
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)

    def scrollDisplayRight(self):
        """ These commands scroll the display without changing the RAM """
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT)

    def leftToRight(self):
        """ This is for text that flows Left to Right """
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def rightToLeft(self):
        """ This is for text that flows Right to Left """
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def autoscroll(self):
        """ This will 'right justify' text from the cursor """
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def noAutoscroll(self):
        """ This will 'left justify' text from the cursor """
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def write4bits(self, bits, char_mode=False):
        """ Send command to LCD """
        self.delayMicroseconds(1000)  # 1000 microsecond sleep
        bits = bin(bits)[2:].zfill(8)
        self.GPIO.output(self.pin_rs, char_mode)
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for i in range(4):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i], True)
        self.pulseEnable()
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for i in range(4, 8):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i-4], True)
        self.pulseEnable()

    def delayMicroseconds(self, microseconds):
        seconds = microseconds / float(1000000)  # divide microseconds by 1 million for seconds
        sleep(seconds)

    def pulseEnable(self):
        self.GPIO.output(self.pin_e, False)
        self.delayMicroseconds(1)       # 1 microsecond pause - enable pulse must be > 450ns
        self.GPIO.output(self.pin_e, True)
        self.delayMicroseconds(1)       # 1 microsecond pause - enable pulse must be > 450ns
        self.GPIO.output(self.pin_e, False)
        self.delayMicroseconds(1)       # commands need > 37us to settle

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""
        for char in text:
            if char == '\n':
                self.write4bits(0xC0)  # next line
            else:
                self.write4bits(ord(char), True)

#-------------------------------------------------------

class gsm():
    echo_on = 1
    def __init__(self,serialPort):               #port initialization
        self.serialPort = serialPort

    def sendCommand(self,at_com):
        self.serialPort.write(at_com + '\r')


    def getResponse(self):
        self.serialPort.flushInput()
        self.serialPort.flushOutput()
        if gsm.echo_on == 1:
            response = self.serialPort.readline()  # comment this line if echo off
        response = self.serialPort.readline()
        response = response.rstrip()
        lcd.clear()
        lcd.message(response)
        return response


    def getPrompt(self):
        if gsm.echo_on == 1:
            response = self.serialPort.readline()  # comment this line if echo off
        if (self.serialPort.readline(1) == '>'):
            return True
        else:
            return False


    def sendMessage(self,phone_number, message):
        flag = False
        self.sendCommand('AT+CMGS=\"' + phone_number + '\"')
        time.sleep(0.5)
        print 'SUCCESS'
        self.serialPort.write(message)
        self.serialPort.write('\x1A')  # send messsage if prompt received
        flag = True
        time.sleep(2)
        print self.getResponse
        return flag

def sendGPRSdata():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H:%M:%S")
    gsm_ser = serial.Serial()
    gsm_ser.port = "/dev/ttyAMA0"
    gsm_ser.baudrate = 9600
    GSM = gsm(gsm_ser)
    
    '''attach or detach the device to packet domain service'''
    GSM.sendCommand("AT+CGATT=1\r") 
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE
    
    '''Configure content type as GPRS'''
    GSM.sendCommand("AT+SAPBR=3,1,\"CONTYPE\",\"GPRS\"\r");
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE
    
    '''Configure content type as GPRS'''
    GSM.sendCommand("AT+SAPBR=3,1,\"APN\",\"airtelgprs.com\"\r");
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE
    
    '''Configure barrier profile to open in GPRS context'''
    GSM.sendCommand("AT+SAPBR=1,1\r") 
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE
    
    '''initiate the http service'''
    GSM.sendCommand("AT+HTTPINIT\r") 
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE

    '''Send sensor data to database through PHP url page'''
    GSM.sendCommand("AT+HTTPPARA=\"URL\",\"http://someserverlocation.com/putnewdata.php?")
    GSM.sendCommand("?timestamp=" )
    GSM.sendCommand(timestamp)
    GSM.sendCommand("&ECG=" )
    GSM.sendCommand(sensor_Data[0])
    GSM.sendCommand("&HBT=" )
    GSM.sendCommand(sensor_Data[1])
    GSM.sendCommand("&Temp" )
    GSM.sendCommand(sensor_Data[2])
    GSM.sendCommand("\r\r")
    time.sleep(5)
    if( GSM.getResponse() != 'OK'): return FALSE     

    '''Get http session start '''
    GSM.sendCommand("AT+HTTPACTION=0\r") 
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE
   
    ''' read the data from http server '''
    GSM.sendCommand("AT+HTTPREAD\r") 
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE

    ''' Terminate http service '''
    GSM.sendCommand("AT+HTTPTERM\r") 
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE     
    
#-----------------------------------------------------------------------------------------------
def gsm_init():
    ''' select GSM_SERIAL communication'''
    #GPIO.output(GSM_SERIAL, GPIO.HIGH)
    #GPIO.output(GARDUNO_SERIAL, GPIO.LOW)
    
    gsm_ser = serial.Serial()
    gsm_ser.port = "/dev/ttyAMA0"
    gsm_ser.baudrate = 9600
    gsm_ser.timeout = 3
    gsm_ser.xonxoff = False
    gsm_ser.rtscts = False
    gsm_ser.bytesize = serial.EIGHTBITS
    gsm_ser.parity = serial.PARITY_NONE
    gsm_ser.stopbits = serial.STOPBITS_ONE
#---------------------------------------------------------------------
    
    try:
        gsm_ser.open()
        gsm_ser.flushInput()
        gsm_ser.flushOutput()

        
    except:
        print 'Cannot open serial port'
        sys.exit()

    print 'GSM Checking ...'
    GSM = gsm(gsm_ser)
    GSM.sendCommand("AT+IPR=9600;&W")
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE
    
    """set SMS text Format"""
    GSM.sendCommand("AT+CMGF=1;&W")   
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE
    
    """Network registriation"""
    GSM.sendCommand("AT+CREG?")        
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE
    
    """Network attach or detach the device to packet domain service"""
    GSM.sendCommand("AT+CGATT=1\r")     
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE

    ''' command brings up the GPRS'''
    GSM.sendCommand("AT+CIICR\r")
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE

    GSM.sendCommand("AT+CIFSR\r")
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE

    GSM.sendCommand("AT+CIPSPRT=1\r")
    time.sleep(0.5)
    if( GSM.getResponse() != 'OK'): return FALSE

    
#----------------------------------------------------------------------------------

def checkAnyCritical():
    '''Select the Modem Serial'''
    #GPIO.output(GSM_SERIAL, GPIO.HIGH)
    #GPIO.output(GARDUNO_SERIAL, GPIO.LOW)
    
    gsm_ser = serial.Serial()
    gsm_ser.port = "/dev/ttyAMA0"
    gsm_ser.baudrate = 9600
    gsm_ser.timeout = 3
    gsm_ser.xonxoff = False
    gsm_ser.rtscts = False
    gsm_ser.bytesize = serial.EIGHTBITS
    gsm_ser.parity = serial.PARITY_NONE
    gsm_ser.stopbits = serial.STOPBITS_ONE
    
    GSM = gsm(gsm_ser)

    ''' Check for any alert '''
    if i == 1 and int(sensor_Data[i]) > 95:
        for i in emergency_Dial:            
            GSM.sendMessage(emergency_Dial[i],"Alert: Critical Heart Rate Ditected for Patient")
        send_mail(emailId, "Critical Heart Rate Ditected for Patient")
    
    elif i == 2 and int(sensor_Data[i]) > 55:
        for i in emergency_Dial:
            GSM.sendMessage(emergency_Dial[i],"Alert: Critical Body Temparature Ditected for Patient")
        send_mail(emailId, "Critical Body Temparature Ditected for Patient")
   
                                
#----------------------------------------------------------------------------------

def requestForSensorData():
    ''' select ARDUNO_SERIAL communication'''
    #GPIO.output(ARDUNO_SERIAL, GPIO.HIGH)
    #GPIO.output(GSM_SERIAL, GPIO.LOW)   
    
    ARDUNO_SER = serial.Serial()
    ARDUNO_SER.port = "/dev/ttyAMA0"
    ARDUNO_SER.baudrate = 9600
    ARDUNO_SER.timeout = 3
    ARDUNO_SER.xonxoff = False
    ARDUNO_SER.rtscts = False
    ARDUNO_SER.bytesize = serial.EIGHTBITS
    ARDUNO_SER.parity = serial.PARITY_NONE
    ARDUNO_SER.stopbits = serial.STOPBITS_ONE
    
    
    #Sending Data to serial
    ARDUNO_SER.adrino.write("DATARQST")
    
    '''insert sensor values into list'''    
    for i in range(1,3):
        sensor_Data.insert(i, adrino.read())

#----------------------------------------------------------------------------------
    
if __name__ == "__main__":
    lcd = Adafruit_CharLCD()
    lcd.clear()
   
    time.sleep(3)
    gsm_init()
   
    time.sleep(3)
    
    while True:
        requestForSensorData()
        checkAnyCritical()
        sendGPRSdata()
        time.sleep(120)
       