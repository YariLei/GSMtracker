import time
import math
import sys
from pygsm import GsmModem

# To switch GPS on or off
def GPSon():
	print "GPS is switched ON"
	reply = gsm.command('AT+CGNSPWR=1')
	print reply
	print

def GPSoff():
	print "GPS is switched OFF"
	reply = gsm.command('AT+CGNSPWR=0')
	print reply
	print
    
def SendStartMessage(id)
	reply = gsm.command('AT+CGNSINF')
	list = reply[0].split(",")
	UTC = list[2][8:10]+':'+list[2][10:12]+':'+list[2][12:14]
	Latitude = list[3]
	Longitude = list[4]
	Altitude = list[5]
	print 'Position: ' + UTC + ', ' + Latitude + ', ' + Longitude + ', ' + Altitude
	Message = ' SMS' + id + ' Service started. Position: ' + UTC + ', ' + str(Latitude) + ', ' + str(Longitude) + ', ' + str(Altitude) + ' http://maps.google.com/?q=' + str(Latitude) + ',' + str(Longitude)
	print "Sending SMS to phone number " + MobileNumber + ": " + Message
	gsm.send_sms(PhoneBackup, Message)

def SendMessage(id):
	reply = gsm.command('AT+CGNSINF')
	list = reply[0].split(",")
	# First check if receiving proper signal from the GSM/GPS module
	if len(list[2]) > 14:
		UTC = list[2][8:10]+':'+list[2][10:12]+':'+list[2][12:14]
		Latitude = list[3]
		Longitude = list[4]
		Altitude = list[5]
		print 'Position: ' + UTC + ', ' + Latitude + ', ' + Longitude + ', ' + Altitude
		
		# Check if receiving altitude figures
		if Altitude <> '':
			Latitude = float(Latitude)
			Longitude = float(Longitude)
			Altitude = float(Altitude)

			# Check altitude vs. maximum allowed
			if Altitude <= MaxAlt:				
				# Send the message burst
				Message = 'HAB:' + PayloadID + ',1,' + UTC + ',' + str(Latitude) + ',' + str(Longitude) + ',' + str(int(Altitude))
				print "Sending to HabHub receiver at " + ReceiverOne + ": " + Message
				gsm.send_sms(ReceiverOne, Message)
				time.sleep(5)
				Message = 'HUB:' + PayloadID + ' SMS' + id + '. Position: ' + UTC + ', ' + str(Latitude) + ', ' + str(Longitude) + ', ' + str(Altitude)
				print "Sending to Alternative Receiver " + ReceiverTwo + ": " + Message
				gsm.send_sms(ReceiverTwo, Message)
				time.sleep(5)
				# Send to backup phone once every 4th message burst
				if (id%4==0)
					Message = PayloadID + ' SMS' + id + '. Position: ' + UTC + ', ' + str(Latitude) + ', ' + str(Longitude) + ', ' + str(Altitude) + ' http://maps.google.com/?q=' + str(Latitude) + ',' + str(Longitude)
					print "Sending to Backup Phone " + PhoneBackup + ": " + Message
					gsm.send_sms(PhoneBackup, Message)

ReceiverOne = "+3584579227310"
ReceiverTwo = "+3584576330859"
PhoneBackup = "+358411362689"
MaxAlt = 2000
LastSMS = 'Start'
MessageID = 0
PayloadID = 'LUT/LeinonenS'

# Boot the device
gsm = GsmModem(port="/dev/ttyAMA0")
gsm.boot()

# Print modem specifications
print "Modem:"
reply = gsm.hardware()
print "Manufacturer = " + reply['manufacturer']
print "Model = " + reply['model']

# Fetch phone number
reply = gsm.command('AT+CNUM')
if len(reply) > 1:
	list = reply[0].split(",")
	phone = list[1].strip('\"')
	print "Number is " + phone
	print

print "Cleaning up old messages"
gsm.query("AT+CMGD=70,4")
print

GPSon()

print "Booted successfully, starting SMS operation."

SendStartMessage(MessageID)

while True:
        
    # Check for SMS commands
	message = gsm.next_message()
	
	if message:
		print message
		text = message.text
		if text[0:5] == 'Start':
			print "SMS operation started"
			GPSon()
			SendStartMessage(MessageID)
			MessageID = MessageID + 1
			SendMessage(MessageID)
			MessageID = MessageID + 1
			LastSMS = 'Start'
			time.sleep(290)
       		elif text[0:4] == 'Stop':
			print "SMS operation halted"
			GPSoff()
			LastSMS = 'Stop'
	else:
		if LastSMS == 'Start':
			SendMessage(MessageID)
			MessageID = MessageID + 1
			time.sleep(290)
		else:
			time.sleep(60)