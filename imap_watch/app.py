#!/usr/bin/env python

import os, os.path, sys
import ConfigParser
import imaplib, email
import pkg_resources as pkg

notifier = None
icon_path = pkg.resource_filename('imap_watch', 'mail.png')

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
	config.set('inbox', 'growl', False)
	config.set('inbox', 'markseen', False)
	with open(path, 'w') as f:
		config.write(f)

def check_folder(section, config):
	port = config.getint(section, 'port')
	secure = config.getboolean(section, 'secure')
	markseen = config.getboolean(section, 'markseen')
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
	
	status, result = client.select(mailbox, readonly=not(config.getboolean(section, 'markseen')))
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

def notify(section, config, msg):
	if(config.get(section, 'growl')):
		global notifier
		if not(notifier):
			import Growl
			notifier = Growl.GrowlNotifier(
				applicationName = 'imap-watch',
				notifications = ['New Message'],
				defaultNotifications = None,
				applicationIcon = Growl.Image.imageFromPath(icon_path),
			)
			notifier.register()
		notifier.notify('New Message', msg['from'], msg['subject'], sticky=True)
	else:
		print '[%s] %s: %s' % (section, msg['from'], msg['subject'])

def main():
	config_path = os.path.join(os.getenv('HOME'), '.imap-watch')
	if not(os.path.exists(config_path)):
		create_sample_config(config_path)
		log("A sample config was created in %s. Modify it and try again." % config_path)
		sys.exit(1)
	
	config = ConfigParser.RawConfigParser()
	config.read(config_path)
	
	for section in config.sections():
		if(config.get(section, 'growl')):
			try:
				import Growl
			except ImportError, e:
				log(section + ': growl_py >= 0.0.7 is not properly installed.')
				sys.exit(1)
	
	for section in config.sections():
		for msg in check_folder(section, config):
			notify(section, config, msg)

