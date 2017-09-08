#!/usr/bin/python
#_*_ coding: utf-8 _*_

# 2017-01-17	fixed unichr ä ö ü
# 2017-01-18	fixed inch descriptors " and '
# 2017-06-12	changed message text to English

try:
	import urllib2
	from bs4 import BeautifulSoup
	import sys
	import unicodedata
	import os
except:
	print ("error: library missing")
	exit()

if ( len(sys.argv) < 2 ):
	print ( "usage:")
	print ("\tdigitec-daily-alert [telegram name]")
	exit()

try:
	# the digitec website wants some request headers,
	# otherwise, it will answer with a '403 Forbidden'
	# https://stackoverflow.com/questions/13303449/urllib2-httperror-http-error-403-forbidden#13303773
	url = "https://digitec.ch/en/liveshopping"
	hdr = {	'Host': 'www.digitec.ch',
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'en-US,en;q=0.5',
			'DNT': '1',
			'Referer': 'https://www.digitec.ch/de/LiveShopping',
			'Connection': 'keep-alive',
			'Cache-Control': 'max-age=0'}

	try:
		request = urllib2.Request(url, headers=hdr)
		response = urllib2.urlopen(request).read()
		parsed_html = BeautifulSoup(response, "lxml")
	except:
		print ("error: cannot open the provided url")
		exit()

	offer_list = parsed_html.body.find("article", attrs={"class", "daily-offer-new"})
	offer = offer_list.find("h5", attrs={"class", "product-name"}).text
	offer = offer.replace("\r", "").replace("\n", " ").replace(" ", "", 1)
	
	url = offer_list.find("a", attrs={"class", "product-overlay"})
	href = url["href"]

	u_raw_price = offer_list.find("div", attrs={"class", "product-price"}).text
	# possibilities:
	# CHF 333.–statt vorher 399.–3
	# CHF 24.90
	# CHF 48.–UVP 54.–1

	# https://unicode-table.com/de/search/?q=%E2%80%93
	# unicode: – 
	# unicode: en dash
	# unicode: u+2013
	# unicode: &#8211
	# unicode: E2 80 93
	price_str_raw = u_raw_price.replace(unichr(8211), "00")					# replace .– with .00
	price_str_raw = price_str_raw.replace("CHF ", "").replace("CHF", "")	# remove CHF
	# cut off at the last number, that means two chars after the dot 
	dex = price_str_raw.find(".") + 3		# or 3 ?
	s_price = price_str_raw[:dex].replace("\n", "")		# cut off only the number part

	message = "Today's deal of the day:\n" + offer + "\n" + s_price + " CHF\nhttps://digitec.ch" + href
	message = message.encode("utf-8")

	# IMPORTANT !
	# $ telegram-send
	# is a custom script, 
	# you can modify this script to redirect the message part to whatever chanel you seem fit
	for i in range(len(sys.argv)-1) :
		os.system("telegram-send " + sys.argv[i+1] + " \"" + message + "\"" )

# enables abortion of the program by CTRL + C
except KeyboardInterrupt:
	print("")
	exit()
