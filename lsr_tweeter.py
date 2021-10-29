import requests
import json
import time
import tweepy
import datetime


api_key = "LGLvv2ngJh8RdnIftvcevHijB"
api_secret = "9dmKI5h3y89GeqpvmDRb5cFwkv2Dmn0b1Nlik61MJKOXEWwkxC"

access_token = "1453483338329559045-HjlbyvuoBWVc2t107eEfcWMPTcX0Hy"
access_secret = "k8ztBxFeLcv3fUJolF0HgGEb9IJXcvPEMmjsNGDFOGP7B"

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)

search_time = 60 # seconds


def tweet(auth,text):
	twitter = tweepy.API(auth)
	twitter.update_status(text)
	print("Tweet sent!")
	print("Sent text:")
	print(text)
	print("\n")


def removeSpaces(phrase):
	words = phrase.split(" ")
	result = ""
	for i, word in enumerate(words):
		if word != '':
			if i == len(words):
				result = result + word
			else:
				result = result + word + " "
	if result == "":
		return "NA"
	else:
		# need to remove any "\r"'s
		result = result.replace('\r','') 
		return result.replace("  "," ") # remove extra spaces in remarks

	
def parseLSR(text):
	# split the full LSR text into individual lines
	lines = text.split("\n")
	# loop through each line and isolate the content that we care about
	for i,line in enumerate(lines):
		if "LOCAL STORM REPORT" in line:
			start = i+1
		if "&&" in line: 
			end = i
		if "..TIME" in line:
			start_omit = i
		if "..REMARKS" in line: 
			end_omit = i+1
	# separate the content we care about into the header & footer info
	header = lines[start:start_omit]
	footer = lines[end_omit:end]
	# get the office ID and time sent info from the header
	office_header = header[0].replace('\r','')
	time_sent = header[1].replace('\r','')

	# Now get the info associated with the individual LSRs. 
	# Note that a single LSR product may contain multiple reports. 
	# We'll split these into individual reports rather than one big one.
	entries = []
	for i,line in enumerate(footer): 
		if line != "": # ignore empty lines
			if line[5:7] == "AM" or line[5:7] == "PM": # take advantage of the fact that each entry starts the same
				entries.append(i)

	# create a dictionary for storing each individual LSR
	LSRs = []
	# loop through each entry and get the relevant info
	for i,e in enumerate(entries): 
		time = removeSpaces(footer[e][0:7])
		rptType = removeSpaces(footer[e][12:29])
		location = removeSpaces(footer[e][29:53])
		latlon = removeSpaces(footer[e][53:])
		date = removeSpaces(footer[e+1][0:12])
		mag = removeSpaces(footer[e+1][12:29])
		county = removeSpaces(footer[e+1][29:48])
		state = removeSpaces(footer[e+1][48:53])
		source = removeSpaces(footer[e+1][53:])

		# Handle the remarks below the main LSR info
		if i+1 != len(entries):
			rmk = footer[e+3:entries[i+1]]
		else: 
			rmk = footer[e+3:]
		remark = ""
		for line in rmk: 
			if line != '': 
				remark = remark + line
		remark = removeSpaces(remark)
		if remark == "" or remark == " ":
			remark = "NA"
		else:
			remark = remark.capitalize()

		report = {
			"office": office_header,
			"time_sent": time_sent,
			"time_valid": time,
			"date": date,
			"location": location,
			"latlon": latlon,
			"county": county,
			"state": state,
			"rptType": rptType,
			"mag": mag,
			"source": source,
			"remark": remark
		}

		LSRs.append(report)

	return LSRs


def iemLSR(auth):
	now = datetime.datetime.utcnow()
	prev = now - datetime.timedelta(seconds=search_time)
	url = "http://mesonet.agron.iastate.edu/json/nwstext_search.py?sts="+datetime.datetime.strftime(prev,"%Y-%m-%dT%H:%M")+"Z&ets="+datetime.datetime.strftime(now,"%Y-%m-%dT%H:%M")+"Z&awipsid=LSR"
	req = requests.get(url)
	newReports = False

	for item in req.json()['results']:
		submitted_time = item['utcvalid']
		#print(submitted_time)
		reports = parseLSR(item['data'])
		details_url = f'forecast.weather.gov/product.php?site=NWS&product=LSR&issuedby={item["cccc"][1:]}'
		details_string = f'...\nFull text: {details_url}'
		if len(reports) > 0: 
			newReports = True
			for report in reports:
				# do some formatting to make it look nice
				source = report["source"][:-1]

				# text version 1
				# text = f'From WFO {item["cccc"][1:]}:\n'\
				# f'Event: {source} reports {report["rptType"].lower()} Mag: {report["mag"]}\n' \
				# f'Where: {report["location"].capitalize()}- {report["state"]}\n' \
				# f'When: {report["time_valid"]}LT {report["date"]}\n' \
				# f'Remarks: {report["remark"].capitalize()}'

				# text version 2
				text = f'From WFO {item["cccc"][1:]}:\n'\
				f'At {report["time_valid"]}LT {report["date"][:-1]}, {source} reports {report["rptType"]}' \
				f'at {report["location"][:-1]}, {report["state"][:-1]}. ' \
				f'Mag: {report["mag"]}\n' \
				f'Remarks: {report["remark"]}'

				# if the report is too long, add a link to the full text
				if len(text) > 280: 
					stop = 280 - len(details_string)
					text = text[0:stop] + details_string

				tweet(auth,text)
	if newReports == False:
		print("No new LSRs in the past "+str(search_time)+" seconds.")

		
def nwsLSR(auth):
	now = datetime.datetime.utcnow() - datetime.timedelta(seconds=search_time)
	req = requests.get("https://api.weather.gov/products/types/LSR")
	output = json.loads(req.text)
	newReports = False
	for report in output['@graph'][0:30]: # only check the last 30 - otherwise you'll check a ton of old reports. 
		report_time = datetime.datetime.strptime(report['issuanceTime'],"%Y-%m-%dT%H:%M:00+00:00")
		if report_time > now:
			newReports = True
			lsr_req = requests.get("https://api.weather.gov/products/"+report['id'])
			lsr_info = json.loads(lsr_req.text)
			#text = parseLSR(lsr_info['productText'])
			reports = parseLSR(lsr_info['productText'])

			office = lsr_info['issuingOffice']
			details_url = f'forecast.weather.gov/product.php?site=NWS&product=LSR&issuedby={office[1:]}'
			details_string = f'...\nFull text: {details_url}'

			for report in reports: 
				# convert each report into a text string
				text = f'{report["office"]} \n'\
				f'Event: {report["source"]}reports {report["rptType"]} Mag: {report["mag"]}\n' \
				f'Where: {report["location"]}- {report["state"]}\n' \
				f'When: {report["time_valid"]}{report["date"]}\n' \
				f'Remarks: {report["remark"]}'

				# if the report is too long, add a link to the full text
				if len(text) > 280: 
					stop = 280 - len(details_string)
					text = text[0:stop] + details_string

				# tweet the LSR
				#tweet(auth,text)
	if newReports == False:
		print(f'No new reports in the past {search_time} seconds')
				
#nwsLSR(auth)
iemLSR(auth)


# LSR Formatting 
# 0         1         2         3         4         5         6         7
# 01234567890123456789012345678901234567890123456789012345678901234567890
# ..TIME...   ...EVENT...      ...CITY LOCATION...     ...LAT.LON...
# ..DATE...   ....MAG....      ..COUNTY LOCATION..ST.. ...SOURCE....
#             ..REMARKS..

# 1115 AM     NON-TSTM WND GST 1 ESE SCOTT STATE LAKE  38.68N 100.90W
# 10/28/2021  M58 MPH          SCOTT              KS   MESONET 

"""
time = 0:7
type = 12:29
location = 29:53
latlon = 53:end
date = 0:12
mag = 12:29
state = 48:53
source = 53:end
"""