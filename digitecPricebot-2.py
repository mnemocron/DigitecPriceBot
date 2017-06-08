#!/usr/bin/python
#_*_ coding: utf-8 _*_

'''
@file 			digitecPricebot-2.py
@brief 			script to fetch product prices from digitec.ch to separate .csv files
@author 		Simon Burkhardt - simonmartin.ch - mnemocron - github.com/mnemocron
@date 			2017.04.18
@description 	made for use with Python 2.7.9
				you can fetch digitec.ch and galaxus.ch products equaly
'''


# ===== COLORS =====
# Print in terminal with colors using Python?
# https://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class bcolors:
    HEADER = '\033[95m'		# purple
    OKBLUE = '\033[94m'		# blue
    OKGREEN = '\033[92m'	# green
    WARNING = '\033[93m'	# yellow
    FAIL = '\033[91m'		# red
    ENDC = '\033[0m'		# white / reset
    BOLD = '\033[1m'		# bold
    UNDERLINE = '\033[4m'	# underline

class product:
	url = ""
	artnr = ""
	name = ""
	price = 0.0
	writeToFile = False

# ===== MODULES =====
try:
	import sys 						# args
	import optparse 				# argument parser
	import os 						# files, directories
	import datetime 				# timestamp
	import urllib2 					# requesting webpages
	from bs4 import BeautifulSoup 	# parsing html
except Exception, ex:
	print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] Error: " + str(ex))
	exit()

# ===== ARGUMENTS =====
parser = optparse.OptionParser('digitecPricebot-2 -i [input file] ( -u [url] ) -o [output directory]')
parser.add_option('-i', '--input-file', dest='infile', type='string', help='specify the input file containing the source urls')
parser.add_option('-o', '--optut-dir',  dest='outdir', type='string', help='specify the output file directory')
parser.add_option('-u', '--url', dest='url', type='string', help='specify a single url to fetch')
parser.add_option('-t', '--ignore-time', dest='ignoreTime', help='update the price tag in the file even if it has already been updated today', action='store_true')

(opts, args) = parser.parse_args()

if ( len(sys.argv) < 2 ) :
	parser.print_help()
	exit(-1)

# check if outdir exists and has write access
if ( opts.outdir is None ) :
	print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] Error: Missing output directory argument")
	exit(-1)
if not ( os.path.isdir(opts.outdir) ) :
	print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] Error: Could not find output directory " + str(opts.outdir))
	exit(-1)
if not ( os.access(opts.outdir, os.W_OK) ) :
	print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] Error: Could not access output directory " + str(opts.outdir))
	exit(-1)

# check if an input source is provided, and if it has read access
if ( opts.url is None ) :
	if not os.path.isfile(opts.infile) or not os.access(opts.infile, os.R_OK):
		print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] Error: Could not access input file " + str(opts.infile))
		exit()

# ===== GET DIGITEC PRICE =====
def getDigitecPrice(url):
	if ( "digitec" in url or "galaxus" in url ) :
		# the digitec website wants some request headers,
		# otherwise, it will answer with a '403 Forbidden'
		# https://stackoverflow.com/questions/13303449/urllib2-httperror-http-error-403-forbidden#13303773
		hdr = {	'Host': 'www.digitec.ch',
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Language': 'en-US,en;q=0.5',
				'DNT': '1',
				'Referer': 'https://www.digitec.ch/',
				'Connection': 'keep-alive',
				'Cache-Control': 'max-age=0'}
		try:
			request = urllib2.Request(url, headers=hdr)
			response = urllib2.urlopen(request).read()
			parsed_html = BeautifulSoup(response, "lxml")
		except Exception, ex:
			print("[" + bcolors.WARNING + "*" + bcolors.ENDC + "] Warning: Could not open url " + url)

		p_artnr = parsed_html.body.find("div", attrs={"class", "product-article-number"}).text.split(" ")[1]
		p_brand = parsed_html.body.find("h1", attrs={"class", "product-name"}).text.replace("\n", "", 1).replace("\n", " ", 1).replace("\n", "")
		# possibilities for p_price:
		# CHF 333.–statt vorher 399.–3
		# CHF 24.90
		# CHF 48.–UVP 54.–1

		# https://unicode-table.com/de/search/?q=%E2%80%93
		# unicode: – / en dash / u+2013 / &#8211 / E2 80 93
		p_price = parsed_html.body.find("div", attrs={"class", "product-price"}).text.replace("\n", "")
		if ( len(p_price) > 3 ) :		# it happens that products don't have price tag
			p_price = p_price.split("CHF")[1].replace(" ", "").replace(unichr(8211), "00")
		else:
			p_price = "0.00"
		# 174.00MSRP291.001 <- cut away two chars after first occurrence of '.'
		p_price = p_price[0:(p_price.find(".")+3)]
		# print (p_artnr + "-" + p_brand.split("(")[0] + " : " + p_price)
		product.url = url
		product.artnr = p_artnr
		product.name = p_brand
		product.price = float(p_price)
		product.writeToFile = True
	else:
		print("[" + bcolors.WARNING + "*" + bcolors.ENDC + "] Warning: Omitting url " + url)
		product.writeToFile = False

# ===== WRITE TO FILE =====
def writeToFile():
	filename = ""
	today = str(datetime.date.today()).replace("-", ".")	# dateformat: yyyy.mm.dd
	for file in os.listdir(opts.outdir) :					# check if a file containing the article number exists
		if ( product.artnr in file ) :
			filename = file
	if ( len(filename) < 2 ) :								# file inexistent in outdir
		filename = (opts.outdir + "/" + product.artnr + "-" + product.name.replace("/", "").split(" (")[0] + ".csv").replace("//", "/")

		with open(filename, 'w+') as csvfile:				# open in write mode + create if inexistent
			csvfile.write("URL\t" + product.url.replace("\n", "") + "\n")		# write header information
			csvfile.write("Art-Nr\t" + product.artnr + "\n")
			csvfile.write("Product\t" + product.name + "\n")
			csvfile.write(today + "\t" + '{:.2f}'.format(product.price) + "\n")		# print two decimal places
		print("[" + bcolors.OKGREEN + "+" + bcolors.ENDC + "] Created: " + product.artnr + " : " + product.name.split("(")[0] + " : " + '{:.2f}'.format(product.price) + " CHF")
	else :
		filename = (opts.outdir + "/" + filename).replace("//", "/")
		# find out if the file was updated today
		updatedToday = False
		with open(filename, 'rb') as csvfile:
			csvfile.seek(-2, 2)							# Jump to the second last byte.
			while ( csvfile.read(1) != b"\n" ) :		# Until EOL is found...
				csvfile.seek(-2, 1)						# jump back the read byte plus one more.
			lastline = csvfile.readline()
			if ( str(today) in lastline ) :
				updatedToday = True

		# only append to file, if the file hasn't been updated today, or the user requested to ignore the date
		if ( not updatedToday or (updatedToday and opts.ignoreTime) ):
			with open(filename, 'a') as csvfile:					# open in append mode
				csvfile.write(today + "\t" + '{:.2f}'.format(product.price) + "\n")
			print("[" + bcolors.OKGREEN + "+" + bcolors.ENDC + "] Updated: " + product.artnr + " : " + product.name.split("(")[0] + " : " + '{:.2f}'.format(product.price) + " CHF")
		else:
			print("[" + bcolors.WARNING + "*" + bcolors.ENDC + "] Warning: Ignoring article " + product.artnr + ", since it was already updated today\n\t\t Use: -t or --ignore-time to force an update")

# ===== MAIN =====
def main():
	try:
		if not ( opts.url is None ) :
			getDigitecPrice(opts.url)
			if ( product.writeToFile ) :
				writeToFile()
		else:
			with open(opts.infile) as listUrl:
				for lineUrl in listUrl:
					# print (bcolors.FAIL + lineUrl + bcolors.ENDC)
					getDigitecPrice(lineUrl)
					if ( product.writeToFile ) :
						writeToFile()

		exit(0)

	# enables abortion of the program through CTRL + C
	except KeyboardInterrupt:
		print("")
		exit(0)

if __name__ == '__main__':
	main()
