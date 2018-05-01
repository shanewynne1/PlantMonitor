from twython import *
import twitter_keys as tk
import time
import grovepi
import subprocess
import math

#create a Twython object by passing the necessary secret API keys
twitter = Twython(tk.consumer_key, tk.consumer_secret, tk.access_token, tk.token_secret)
twitter.verify_credentials()

#get read of latest tweets for 'herbs'
search = twitter.search(q='herbs', count=10)
tweets = search['statuses']
    

#analog sensor port number
moisture_sensor			= 1
light_sensor			= 2

#digital sensor
temp_humidity_sensor	= 4

#temp_himidity_sensor type
blue=0

time_to_sleep		= 5
log_file="plant_monitor_log.csv"

#Read the data from the sensors
def read_sensor():
	try:
		moisture=grovepi.analogRead(moisture_sensor)
		light=grovepi.analogRead(light_sensor)
		[temp,humidity] = grovepi.dht(temp_humidity_sensor,blue)
		#Return -1 in case of bad temp/humidity sensor reading
		if math.isnan(temp) or math.isnan(humidity):		#temp/humidity sensor sometimes gives nan
			return [-1,-1,-1,-1]
		return [moisture,light,temp,humidity]
	
	#Return -1 in case of sensor error
	except IOError as TypeError:
			return [-1,-1,-1,-1]

while True:
	curr_time_sec=int(time.time())
	
	#output 10 tweets to terminal
	for tweet in tweets:
            print tweet['id_str'], '\n', tweet['text'], '\n\n\n'
            
	
	# If it is time to take the sensor reading
	if curr_time_sec>1:
		[moisture,light,temp,humidity]=read_sensor()
		# If any reading is a bad reading, skip the loop and try again
		if moisture==-1:
			print("Bad reading")
			time.sleep(1)
			continue
		curr_time = time.strftime("%Y-%m-%d:%H-%M-%S")
		print(("Time:%s\nMoisture: %d\nLight: %d\nTemp: %.2f C\nHumidity:%.2f %%\n" %(curr_time,moisture,light,temp,humidity)))
		
		# Save the sensor reading to the CSV file
		f=open(log_file,'a')
		f.write("%s,%d,%d,%.2f,%.2f;\n" %(curr_time,moisture,light,temp,humidity))
		f.close()
	
	
                #post to twitter
                twitter.update_status(status="Time:%s\nMoisture: %d\nLight: %d\nTemp: %.2f C\nHumidity: %.2f %%\n" %(curr_time,moisture,light,temp,humidity))
	
	#Slow down the loop
	time.sleep(time_to_sleep)
