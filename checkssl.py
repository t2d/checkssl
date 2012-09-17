#!/usr/bin/env python

import os.path
import subprocess
import re

useTor = 1
verbose = 0
siteDir = "/etc/apache2/sites-enabled"

sites = os.listdir(siteDir)
websites = []

class Website(object):
	Checkable = 0
	
	def __init__(self, name):
		self.Name = name
	
	def setCert(self, cert):
		self.Cert = cert
	
	def isCheckable(self):
		self.Checkable = 1


for site in sites:
	
	ssl = 0
	# get sitenames and certfiles
	sitePath = os.path.join(siteDir, site)
	fobj = open(sitePath, "r")
	for line in fobj:
		line = line.strip()
		if ssl == 0:
			if re.match("<VirtualHost.*:443>", line):
					ssl = 1
		elif ssl == 1:
			if re.match("ServerName", line) and ssl == 1:
				name = line.split()[1]
				website = Website(name)
				websites.append(website)
			elif re.match("SSLCertificateFile", line):
				cert = line.split()[1]
				website.setCert(cert)
			elif re.match("</VirtualHost>", line):
				ssl = 0
	fobj.close()

for website in websites:

	# build command
	args = ["openssl s_client -connect ", website.Name, ":443 -CAfile ", website.Cert]
	if useTor == 1:
		args.insert(0, "torify ")
	command = ''.join(args)
	if verbose == 1:
		print command
	# evil shell=True
	sslcheck = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	output = sslcheck.communicate("QUIT")[0]
	
	# check verfication status
	outlist = output.split('\n')
	for line in outlist:
		line = line.strip()
		if re.match("Verify return code", line):
			website.Checkable = 1
			status = line.split()[3]
			if status != '0':
				print website.Name + ": " + line
			else:
				if verbose == 1:
					print website.Name + " okay"
				
	if website.Checkable == 0:
		print "unable to check " + website.Name
