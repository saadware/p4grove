import sys
import urllib
import urllib2
from optparse import OptionParser
from P4 import P4,P4Exception

def main():
	#parse some stuff
	parser = OptionParser(usage="usage: %prog [options] change server:port user client groveUrl", version="%prog 1.0")
	parser.add_option( "-w", 
			"--whatif", 
			action="store_true", 
			dest="whatif", 
			help="does not execute the http post to grove but shows output" )
	parser.add_option( "-p", 
			"--p4WebUrl", 
			action="store", 
			dest="p4WebUrl", 
			help="perforce web (p4web) url")
	parser.add_option( "-b", 
			"--botName", 
			action="store", 
			dest="botName",
			default="P4Bot",
			help="name of Bot that displays on grove channel")
	(options, args) = parser.parse_args()

	# ensure our requied args are there
	if len(args) != 5:
		parser.error( "bad number of arguments" )
	
	# init with arguments
	p4 = P4()
	change = args[0]
	p4.port = args[1]
	p4.user = args[2]
	p4.client = args[3]
	groveUrl = args[4]

	# connect up and run to get the p4 change information
	cl = []
	try:
		p4.connect()
		cl = p4.run_changes( '-l', ("//...@%s,@%s" % (change, change)) )
	except P4Exception:
		print "An error occured somewhere..."
		for e in p4.errors:
			print e
		for w in p4.warnings:
			print w
	finally:
		p4.disconnect()

	# continue if we have a valid change
	if len(cl) < 1:
		exit("ERROR: bad change list %s" % change)

	# extract information and build up our irc message to post to grove
	p4User = cl[0]['user']
	msg = "p4 commit: %s submitted change %s" % (p4User, change)
	if options.p4WebUrl != None:
		msg = "%s (%s/%s?ac=10)" % (msg, options.p4WebUrl, change)
	p4Desc = cl[0]['desc']
	p4Desc = p4Desc[0: 480 - len(msg)]
	msg = "%s : '%s'" % (msg, p4Desc)

	# these are the data pieces the grove API exposes; init and encode
	groveValues = { 'service': options.botName, 
			'message' : msg, 
			'url': 'http://perforce.com', 
			'icon_url' : 'http://perforce.com/sites/default/files/perforce_favicon.png' }
	postData = urllib.urlencode( groveValues )

	# show what would be posted or actually execute
	if options.whatif:
		print msg
		print groveValues
		print postData
	else:
		req = urllib2.Request( groveUrl, postData )
		res = urllib2.urlopen( req )
		res.read()

if __name__ == "__main__":
	main()
