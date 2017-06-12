#!/usr/bin/python
#_*_ coding: utf-8 _*_
try:
	import urllib2
	from bs4 import BeautifulSoup
	import sys
	import unicodedata
	import os
except:
	print ("error: library missing")
	exit()

if ( len(sys.argv) < 3 ):
	print ( "usage:" )
	print ("\tdigitec-alert [digitec url] [max price]")
	print ("\tdigitec-alert [digitec url] [max price] [telegram name]")
	exit()

try:
	max_price = float(sys.argv[2])
except ValueError:
	print ("error: cannot convert \"" + sys.argv[2] + "\" to a numeral value")
	exit()

try:
	# the digitec website wants some request headers,
	# otherwise, it will answer with a '403 Forbidden'
	# https://stackoverflow.com/questions/13303449/urllib2-httperror-http-error-403-forbidden#13303773
	url = sys.argv[1]
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

	u_raw_price = parsed_html.body.find("div", attrs={"class", "product-price"}).text
	u_raw_name = parsed_html.body.find("h1", attrs={"class", "product-name"}).text
	# \nBrandname\nProductname\n -> Brandname Productname
	u_raw_name = u_raw_name.replace("\n", "", 1).replace("\n", " ", 1).replace("\n", "")

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

	try:
		f_price = float(s_price)
	except ValueError:
		print ("error: cannot find a numeral price value")
		exit()

	if ( f_price <= max_price) :
		message = "The product \"" + u_raw_name + "\" costs only " + s_price + " CHF" + " (your specified price: " + sys.argv[2] + ")"
		print (message)
		telegram_msg = message.replace("\"", "\\\"") + "\\n" + sys.argv[1]
		# if optional name is present, send via telegram
		if ( len(sys.argv) > 3 ) :
			# telegram-send  [user] ["msg"]
			os.system("telegram-send " + sys.argv[3] + " \"" + telegram_msg + "\"" )

# enables abortion of the program by CTRL + C
except KeyboardInterrupt:
	print("")
	exit()
