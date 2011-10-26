#!/usr/bin/env python

# Get the latest version from http://devel.ifca.es/~alvaro/files/ggus_generate_report.py
# AUTHOR: Alvaro Lopez <aloga@ifca.unican.es>

__version__ = 20110530

import urllib
import urllib2

import time

from xml.dom import minidom

import sys
import getopt

def usage():
    print """usage: %s <username> <password> [-r] [-h]
    Options:
        -r  Reverse sort (oldest first)
        -h  Show this help
    """ % sys.argv[0]


try:
    opts, args = getopt.getopt(sys.argv[1:], 'rh')
except getopt.GetoptError, err:
    print >> sys.stderr, "ERROR: " + str(err)
    usage()
    sys.exit(1)

reverse = False
for o, a in opts:
    if o == "-h":
        usage()
        sys.exit(0)
    elif o == "-r":
        reverse = True

if len(args) != 2:
    print "ERROR. Usage %s <username> <password>" % sys.argv[0]
    sys.exit(1)

login = args.pop(0)
password = args.pop(0)

login_data = {'login': login, 'pass': password}

url_login = 'https://ggus.eu/admin/login.php'
url_xml = 'https://ggus.eu/ws/ticket_search.php?writeFormat=XML&&show_columns_check=Array&ticket=&supportunit=NGI_IBERGRID&vo=all&user=&keyword=&involvedsupporter=&assignto=&affectedsite=&specattrib=0&status=open&priority=all&typeofproblem=all&mouarea=&radiotf=1&timeframe=any&from_date=&to_date=&untouched_date=&orderticketsby=GHD_INT_REQUEST_ID&orderhow=descending&show_columns=REQUEST_ID;TICKET_TYPE;AFFECTED_VO;AFFECTED_SITE;PRIORITY;RESPONSIBLE_UNIT;STATUS;DATE_OF_CREATION;LAST_UPDATE;TYPE_OF_PROBLEM;SUBJECT'

message_header = """
### Open GGUS tickets ###

There are %(nr_of_tickets)s open tickets under IBERGRID scope. Please find below a
short summary of those tickets. Please take the appropriate actions:
    - Change the ticket status from "ASSIGNED" to "IN PROGRESS".
    - Provide feedback on the issue as regularly as possible.
    - In case of problems, ask for help in ibergrid-ops@listas.cesga.es
    - For long pending issues, put your site/node in downtime.
    - Don't forget to close the ticket when you have solved the problem."""

ticket_body = """
===============================================================================
SITE : * %(affected_site)s *
        GGUS ID     : %(request_id)s
        Open since  : %(date_of_creation)s UTC
        Status      : %(status)s
        Description : %(subject)s
        Link        : https://gus.fzk.de/ws/ticket_info.php?ticket=%(request_id)s
==============================================================================="""


opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
urllib2.install_opener(opener)

# Make login
login_data = urllib.urlencode(login_data)
f = opener.open(url_login, login_data)
f.close()

# Get the XML report
f = opener.open(url_xml)
report = f.read()
f.close()

xml = minidom.parseString(report)
tickets = xml.getElementsByTagName('ticket')

nr_of_tickets = len(tickets)

print message_header % locals()

if reverse:
    tickets.reverse()

for ticket in tickets:
    affected_site = ticket.getAttribute("affected_site") or "N/A"
    date_of_creation = time.strftime("%B %d %Y %H:%M",time.gmtime(float(ticket.getAttribute("date_of_creation"))))
    status = ticket.getAttribute("status")
    subject = ticket.getElementsByTagName("subject")[0].firstChild.data
    request_id = ticket.getAttribute("request_id")

    print ticket_body % locals()

