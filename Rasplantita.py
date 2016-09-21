import httplib, urllib
from time import localtime, strftime
# download from http://code.google.com/p/psutil/
import psutil
import time

import spidev
import time
import os

import smtplib


import RPi.GPIO as GPIO ## Import GPIO library

GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(7, GPIO.OUT) ## Setup GPIO Pin 7 to OUT



# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

email = 0
L1=100 #limite para regado con bomba
L2=300 #limite para envio de mail

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

def send_email_riego():
            gmail_user = "carloslrm@gmail.com"
            gmail_pwd = "xxxx"
            FROM = 'carloslrm@gmail.com'
            TO = ['calinenusa@gmail.com'] #must be a list
            SUBJECT ="He regado tu planta"
            TEXT = "Tu planta ha sido regada, por favor verifica que tenga agua el recipiente"
 
            # Prepare actual message
            message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
            try:
                #server = smtplib.SMTP(SERVER) 
                server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
                server.ehlo()
                server.starttls()
                server.login(gmail_user, gmail_pwd)
		server.sendmail(FROM, TO, message)
                #server.quit()
                server.close()
                print ('successfully sent the mail')
            except:
                print ("failed to send mail")

def send_email(num):           
            gmail_user = "carloslrm@gmail.com"
            gmail_pwd = "xxxx"
            FROM = 'carloslrm@gmail.com'
            TO = ['calinenusa@gmail.com'] #must be a list
            SUBJECT ="Tu planta necesita Agua"
            TEXT = "Hola, soy tu planta y necesito agua! Este es el correo No. " + str(num) + " de 5"

            # Prepare actual message
            message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
            try:
                #server = smtplib.SMTP(SERVER) 
                server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
                server.ehlo()
                server.starttls()
                server.login(gmail_user, gmail_pwd)
                server.sendmail(FROM, TO, message)
                #server.quit()
                server.close()
                print ('successfully sent the mail')
            except:
                print ("failed to send mail")


def doit():
	global email
	
	cpu_pc = psutil.cpu_percent()
	#mem_avail_mb = psutil.avail_phymem()/1000000	
	adc_data = ReadChannel(0)

   	#print(cpu_pc)
        print(adc_data)
        print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))


	params = urllib.urlencode({'field1': cpu_pc, 'field2': adc_data,'key':'OLMTB98T40UVJFRH'})
	headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
	conn = httplib.HTTPConnection("api.thingspeak.com:80")

	if adc_data < L1:
		GPIO.output(7,False) ## Encender la bomba
		print ("la bomba deberia estar ON")
		time.sleep(3)

		GPIO.output(7,True)   
		print ("la bomba deberia estar oFF")
		time.sleep(1)


		print ("estoy intentando enviar el mail")
		send_email_riego()
	else:
		if adc_data <L2:
			print("necesito agua, se han enviado " + str(email) + " emails")
			if email < 5:
				email+=1
				send_email(email)
		else:
			print("it's ok")
			email=0
	try:
		conn.request("POST", "/update", params, headers)
		response = conn.getresponse()
		#print(cpu_pc)
		#print(adc_data)
		#print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
		print(response.status, response.reason)
		data = response.read()
		conn.close()
	except:
			print("connection failed")	

#sleep for 16 seconds (api limit of 15 secs)
if __name__ == "__main__":
	time.sleep(1)
	#GPIO.cleanup();
	GPIO.output(7,True)
	
	#GPIO.output(7,True) ## Encender la bomba
        #time.sleep(1)
        #GPIO.output(7,False)
	#time.sleep(1)
        print ("waiting...waiting.. la bomba deberia estar off")

	time.sleep(2)

	while True:
		doit()
		time.sleep(18) 
