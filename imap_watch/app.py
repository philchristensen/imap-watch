#!/usr/bin/env python

import os, os.path, sys, logging
import ConfigParser
import imaplib, email, smtplib
import pkg_resources as pkg
from email import message

log = logging.getLogger(__name__)

FORWARD_TO_EMAIL = 'phil@bubblehouse.org'
SOURCE_EMAIL = 'devs@freelancersunion.org'

def get_client(section, config):
	port = config.getint(section, 'port')
	secure = config.getboolean(section, 'secure')
	host = config.get(section, 'host')
	
	if(secure):
		return imaplib.IMAP4_SSL(host, port)
	else:
		return imaplib.IMAP4(host, port)

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

def get_messages_since(section, config):
	client = get_client(section, config)
	markseen = config.getboolean(section, 'markseen')
	username = config.get(section, 'username')
	password = config.get(section, 'password')
	mailbox = config.get(section, 'mailbox')
	
	status, result = client.login(username, password)
	#('OK', ['LOGIN completed'])
	if(status != 'OK'):
		log.error(result)
		return
	
	status, result = client.select(mailbox, readonly=False)
	#('OK', ['137'])
	if(status != 'OK'):
		log.error(result)
		return
	
	status, result = client.search(None, '(SINCE "30-May-2012")')
	#('OK', [''])
	if(status != 'OK'):
		log.error(result)
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
		log.info("A sample config was created in %s. Modify it and try again." % config_path)
		sys.exit(1)
	
	config = ConfigParser.RawConfigParser()
	config.read(config_path)
	
	section = 'jira'
	messages = list(get_messages_since(section, config))
	username = config.get(section, 'username')
	password = config.get(section, 'password')
	
	smtp = smtplib.SMTP(
		config.get('smtp', 'host'),
		config.get('smtp', 'port'),
		'jawaka.dev.fuwt'
	)
	smtp.set_debuglevel(True)
	
	for msg in messages:
		payload = msg.get_payload()
		forwarded_message = message.Message()
		forwarded_message.set_payload(payload)
		for header, value in msg.items():
			if(header not in ['From', 'To', 'Subject', 'MIME-Version', 'Content-Type', 'Content-Transfer-Encoding']):
				continue
			elif(header == 'From'):
				forwarded_message['From'] = SOURCE_EMAIL
			elif(header == 'To'):
				forwarded_message['To'] = FORWARD_TO_EMAIL
			else:
				forwarded_message[header] = value
		smtp.sendmail(SOURCE_EMAIL, [FORWARD_TO_EMAIL], forwarded_message.as_string())
		break # remove me
	smtp.quit()
