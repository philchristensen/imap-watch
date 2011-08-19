#!/usr/bin/env python

import os, os.path, sys
import ConfigParser
import imaplib, email

def log(msg):
	print >>sys.stderr, str(msg)

def create_sample_config(path):
	config = ConfigParser.RawConfigParser()
	config.add_section('inbox')
	config.set('inbox', 'host', 'mail.example.com')
	config.set('inbox', 'port', 143)
	config.set('inbox', 'secure', False)
	config.set('inbox', 'username', 'joe')
	config.set('inbox', 'password', 'secret')
	config.set('inbox', 'mailbox', 'INBOX')
	with open(path, 'w') as f:
		config.write(f)

def check_folder(section, config):
	port = config.getint(section, 'port')
	secure = config.getboolean(section, 'secure')
	host = config.get(section, 'host')
	username = config.get(section, 'username')
	password = config.get(section, 'password')
	mailbox = config.get(section, 'mailbox')
	
	if(secure):
		client = imaplib.IMAP4_SSL(host, port)
	else:
		client = imaplib.IMAP4(host, port)
	
	status, result = client.login(username, password)
	#('OK', ['LOGIN completed'])
	if(status != 'OK'):
		log(result)
		return
	
	status, result = client.select(mailbox, readonly=True)
	#('OK', ['137'])
	if(status != 'OK'):
		log(result)
		return
	
	status, result = client.search(None, '(UNSEEN)')
	#('OK', [''])
	if(status != 'OK'):
		log(result)
		return
	
	for msg_num in result[0].split():
		if not(msg_num):
			continue
		data = client.fetch(msg_num, "RFC822")
		yield email.message_from_string(data[1][0][1])

def main():
	config_path = os.path.join(os.getenv('HOME'), '.imap-watch')
	if not(os.path.exists(config_path)):
		create_sample_config(config_path)
		log("A sample config was created in %s. Modify it and try again." % config_path)
		sys.exit(1)
	
	config = ConfigParser.RawConfigParser()
	config.read(config_path)
	
	for section in config.sections():
		for msg in check_folder(section, config):
			print '%s: %s' % (msg['from'], msg['subject'])

