# Untitled - By: Swapnil - Tue Aug 3 2021
# Time Lapse Photos (Credit nedhorning)
#
# This example shows off how to take time lapse photos using your OpenMV
# Cam and using the RTC module along with a timer interrupt to achieve
# very low power operation.
#
# Note that if the USB is still plugged in when the camera is taking
# pictures it will run the bootloader each time. Please power the camera
# from something other than USB to not have the bootloader run.

import pyb, machine, sensor, image, pyb, os, time, tf
import network, socket, ustruct, utime

def Open_Socket():
	SSID='Wi-Fi' # Network SSID
	KEY='01859439142225485833'  # Network key

	# Init wlan module and connect to network
	print("Trying to connect... (This may take a while)...")
	wlan = network.WLAN(network.STA_IF)
	wlan.deinit()
	wlan.active(True)
	wlan.connect(SSID, KEY, timeout=30000)
	# We should have a valid IP now via DHCP
	print("WiFi Connected ", wlan.ifconfig())

	# Create new socket
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return client, wlan

def File_Name(rtc):
	# Extract the date and time from the RTC object.
	dateTime = rtc.datetime()
	year = str(dateTime[0])
	month = '%02d' % dateTime[1]
	day = '%02d' % dateTime[2]
	hour = '%02d' % dateTime[4]
	minute = '%02d' % dateTime[5]
	second = '%02d' % dateTime[6]
	subSecond = str(dateTime[7])

	newName='I'+year+month+day+hour+minute+second+'_' # Image file name based on RTC
	return newName

def main():
	# Create and init RTC object. This will allow us to set the current time for
	# the RTC and let us set an interrupt to wake up later on.
	rtc = pyb.RTC()
	newFile = False

	try:
		os.stat('dataset.csv')
	except OSError: # If the log file doesn't exist then set the RTC with NTP and set newFile to True
		client, wlan = Open_Socket()
		addr = socket.getaddrinfo("pool.ntp.org", 123)[0][4]
		# Send query
		client.sendto('\x1b' + 47 * '\0', addr)
		data, address = client.recvfrom(1024)

		# Print time
		TIMESTAMP = 2208988800+946684800
		t = ustruct.unpack(">IIIIIIIIIIII", data)[10] - TIMESTAMP
		print ("Year:%d Month:%d Day:%d Time: %d:%d:%d" % (utime.localtime(t)[0:6]))
		# datetime format: year, month, day, weekday (Monday=1, Sunday=7),
		# hours (24 hour clock), minutes, seconds, subseconds (counds down from 255 to 0)
		# Get addr info via DNS
		rtc.datetime((utime.localtime(t)[0], utime.localtime(t)[1], utime.localtime(t)[2],
					utime.localtime(t)[6], utime.localtime(t)[3], utime.localtime(t)[4],
					utime.localtime(t)[5], 0))
		newFile = True
		client.close()
		wlan.disconnect()

	# Enable RTC interrupts every 10 seconds, camera will RESET after wakeup from deepsleep Mode.
	rtc.wakeup(10000)

	BLUE_LED_PIN = 3

	sensor.reset() # Initialize the camera sensor.
	sensor.set_pixformat(sensor.GRAYSCALE)
	sensor.set_framesize(sensor.QVGA)
	sensor.skip_frames(time = 2000) # Let new settings take affect.

	# Load tf network and labels
	net = "trained.tflite"
	labels = [line.rstrip('\n') for line in open("labels.txt")]

	# Let folks know we are about to take a picture.
	pyb.LED(BLUE_LED_PIN).on()

	# Take photo and perform classification
	img = sensor.snapshot()

	predicted_label = ''
	# default settings just do one detection... change them to search the image...
	for obj in tf.classify(net, img, min_scale=1.0, scale_mul=0.8, x_overlap=0.5, y_overlap=0.5):
		# This combines the labels and confidence values into a list of tuples
		predictions_list = list(zip(labels, obj.output()))
		# Abstract max value and its index from the output
		predictions_max = max(obj.output())
		predictions_max_index = obj.output().index(predictions_max)
		# print("%f at %i" % (predictions_max, predictions_max_index))
		predicted_label = labels[predictions_max_index]
		print(predicted_label)

		for i in range(len(predictions_list)):
			print("%s = %f" % (predictions_list[i][0], predictions_list[i][1]))

	newName = File_Name(rtc) + predicted_label
	if not "images" in os.listdir(): os.mkdir("images") # Make an images directory
	img.save('images/' + newName, quality=100)

	if(newFile): # If dataset file does not exist then create it.
		with open('dataset.csv', 'a') as datasetFile: # Write text file to keep track of image and predictions.
			# Prepare heading
			datasetFile.write('Image_File_Name, ')
			for i in range(len(labels)):
				datasetFile.write(labels[i] + ', ')
			datasetFile.write('Prediction' + '\n')
			# Write 1st observation
			datasetFile.write(newName + ', ')
			for i in range(len(predictions_list)):
				datasetFile.write(str(predictions_list[i][1]) + ', ')
			datasetFile.write(predicted_label + '\n')
	else:
		with open('dataset.csv', 'a') as datasetFile: # Append image and predictions in the dataset file.
			datasetFile.write(newName + ', ')
			for i in range(len(predictions_list)):
				datasetFile.write(str(predictions_list[i][1]) + ', ')
			datasetFile.write(predicted_label + '\n')

	time.sleep_ms(10*1000)
	pyb.LED(BLUE_LED_PIN).off()

	# Enter Deepsleep Mode (i.e. the OpenMV Cam effectively turns itself off except for the RTC).
	machine.deepsleep()

main()
