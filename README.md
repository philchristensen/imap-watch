imap-watch 1.0
==============

19 August 2011

by Phil Christensen

`mailto:phil@bubblehouse.org`

A command-line app to watch IMAP folders. Watch multiple folders across several servers, and
optionally issue Growl notifications when new messages are found.

Installation
------------

Clone the repo:

	git clone git://github.com/philchristensen/imap-watch.git

Install setuptools git support:

	easy_install setuptools_git

If you have a Mac, and want to use Growl notifications, install Growl-py:

	easy_install growl_py

Install the package:

	python setup.py install

Usage
-----

To create a sample config file, run imap-watch once at the command line. This
will generate an INI-based config file in ~/.imap-watch

	[inbox]
	host = mail.example.com
	port = 143
	secure = False
	username = joe
	password = secret
	mailbox = INBOX
	growl = False
	markseen = False

Create as many sections as you want. All options are required; here's one I use to monitor
a folder of Jira notification messages:

	[jira]
	host = mail.myserver.com
	port = 993
	secure = True
	username = phil
	password = *********
	mailbox = Jira
	growl = True
	markseen = True

By setting 'markseen' to True, messages will automatically be marked as seen when a notification
is displayed.

Once you're properly configured, add the following to your crontab:

	*/5 * * * * /opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin/imap-watch

This will scan the IMAP folder every 5 minutes.