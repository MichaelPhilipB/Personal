#------------------------------------------------------------------------
# getdue.py
#
# Queries the RI library server.
# If there are books due soon, sends an email.
#------------------------------------------------------------------------

import cookielib
import copy
import datetime
import formatter
import htmllib
import os
import re
import smtplib
import sys
import traceback
import urllib
import urllib2
import urlparse

#------------------------------------------------------------------------
# A dictionary of names to (email, libarary ID) tuples.
users = {
    "Michael" : ("Michael.Philip.Brady@gmail.com", '21332000671604', '1234'),
    "Eileen"  : ("Eileen.Brady.98@gmail.com",      '21332000729253', '1234'),
    "Owen"    : ("Michael.Philip.Brady@gmail.com", '21332000676587', '1234'),    
    }

#------------------------------------------------------------------------
def parseStatus(status):
    """Parses the 'status' string from the web page.
    """

    status = status.strip()

    # Sometimes there is a stock phrase at the end of the string.
    # Ignore it.
    stockPhrases = [
        'LIB USE ONLY',
        'DISPLAY Renewed 1 time',
        'DISPLAY',
        'Renewed 1 time',
        '+1 HOLD',
        ]
    for stockPhrase in stockPhrases:
        if status.endswith(stockPhrase):
            status = status[:-len(stockPhrase)]
    
    statusElem = status.split()
    if len(statusElem) == 2 and statusElem[0] == "DUE":

        dueDateStr = statusElem[1]
        month, day, year = dueDateStr.split("-")
        month = int(month)
        day = int(day)
        year = 2000 + int(year)
    
        deltaUntilDue = datetime.date(year, month, day) - datetime.date.today()
        
        daysUntilDue = deltaUntilDue.days

    else:
        daysUntilDue = -1

    return daysUntilDue

#------------------------------------------------------------------------
def daysUntilDueStr(days):
    """Returns a string for the given number of days.

    @param days An integer number of days.
    @return A string label.
    """

    if days < 0:
        dayStr = "*** OVERDUE ***"
    elif days == 0:
        dayStr = "today"
    elif days == 1:
        dayStr = "tomorrow" 
    else:
        dayStr = str(days) + " days"
    return dayStr

#------------------------------------------------------------------------
def readBooksPage(libraryId, userPin):
    """Reads the web site, returns the HTML page listing checked out books.

    @param libraryId The library card ID to get checked out books for.
    @param libraryPin The PIN that goes with the ID.
    
    @return The HTML string of the checked out books page.
    """

    # Set up urllib2 to handle cookies.
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor()) 
    urllib2.install_opener(opener)

    # Log in.
    
    url = 'https://catalog.oslri.net/patroninfo'
    url = 'https://catalog.oslri.net/iii/cas/login?service=https%3A%2F%2Fcatalog.oslri.net%3A443%2Fpatroninfo~S1%2FIIITICKET&scope=1'

    # Download the log in page.  We parse a variable from this,
    # and it gets the session cookies set up.
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    responseText = response.read()

    # Find the hidden 'lt' value.
    ltRegex = re.compile('<input type="hidden" name="lt" value="([^"]*)"')
    ltValue = ltRegex.search(responseText).group(1)

    # Post the log in form.
    values = {'code' : libraryId, 'pin' : userPin,
              'lt' : ltValue, '_eventId' : 'submit'}

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)

    # The login page redirects us to the list of held books page.
    #
    # We construct the URL of the checked out books page by
    # replacing the last part of the returned held-books URL with 'items'.
    url = response.geturl()

    urlElems = url.split("/")
    urlElems.pop()
    urlElems.append("items")
    url = "/".join(urlElems)

    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    
    thePage = response.read()

    return thePage

#------------------------------------------------------------------------
def sendGmail(mailTo, mailBody):
    """Sends an email to the specified address with the specified message.

    @param mailTo The address to send the email to.
    @param mailBody The body of the email.
    """

    smtpServer = "smtp.gmail.com"
    #smtpPort = 465
    smtpPort = 587
    smtpUserName = "Michael.Philip.Brady@gmail.com"
    smtpPassword = readPassword()

    mailFrom =  "Michael.Philip.Brady@gmail.com"
    mailSubject = "Barrington Library books due soon"

    mailText = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (mailFrom,
                                                                mailTo,
                                                                mailSubject,
                                                                mailBody)

    server = smtplib.SMTP()
    #server.debuglevel = 5

    server.connect(smtpServer, smtpPort)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtpUserName, smtpPassword)
    server.sendmail(mailFrom, mailTo, mailText)

    # There is an smtp QUIT command, but sending it gives an SSL error.

#------------------------------------------------------------------------
def readPassword():
    '''Reads the password from a file.
    '''

    fileName = os.path.join(os.path.dirname(__file__), 'credential.txt')

    return open(fileName, 'r').read().strip()

#------------------------------------------------------------------------
def readAndSendEmail(userName):
    """Reads the web page and sends an email for the specified user.

    @param userName The user to check library books for.
    """

    userEmail, userLibraryId, userPin = users[userName]

    thePage = readBooksPage(userLibraryId, userPin)
    
    parser = DueDateParser()
    parser.feed(thePage)
    parser.close()
    
    # True if there's an urgent item that requires an email to be sent.
    isUrgentItem = False
    
    for title, daysUntilDue in parser.booksDue:
        if daysUntilDue < 4:
            isUrgentItem = True

    # A dictionary of lists of titles, keyed by days until due.
    dueDict = {}

    for title, daysUntilDue in parser.booksDue:
        if daysUntilDue not in dueDict:
            dueDict[daysUntilDue] = []
        dueDict[daysUntilDue].append(title)

    mailMsg = "Here are your due dates as reported by:\n"
    mailMsg += "https://catalog.oslri.net/patroninfo\n"
    for daysUntilDue in sorted(dueDict.keys()):

        mailMsg += "\n"
        mailMsg += "----------------\n"
        mailMsg += daysUntilDueStr(daysUntilDue) + "\n"
        mailMsg += "----------------\n"

        titles = dueDict[daysUntilDue]
        for title in titles:
            mailMsg += title + "\n"

    if isUrgentItem:
        sendGmail(userEmail, mailMsg)

#------------------------------------------------------------------------
def checkBooks(userName):
    """The main function that should be called.

    @param userName The user to check library books for.
    """

    try:
        readAndSendEmail(userName)
    except Exception, e:
        userEmail, userLibraryId, userPin = users[userName]
        
        msg = "An error occured while checking your library books.  "
        msg += "Please tell Michael about this.\n\n"
        msg += "Error:\n"

        excMsgLines = traceback.format_exception(*sys.exc_info())
        excMsg = "".join(excMsgLines)
        msg += excMsg

        #Un-comment this to see the error for debugging.
        sendGmail(userEmail, msg)

#========================================================================
class DueDateParser(htmllib.HTMLParser):
    """Parses a library HTML page to find book tiles and due dates.
    """

    #--------------------------------------------------------------------
    def __init__(self, verbose=0):
        htmllib.HTMLParser.__init__(self,
                                    formatter.NullFormatter(),
                                    verbose)
        
        # A list of (title, daysUntilDue) tuples.
        self.booksDue = []

        self.inTitle = False
        self.title = None
        self.inStatus = False

    #--------------------------------------------------------------------
    def start_td(self, attrList):
        for name, val in attrList:
            if name == 'class':
                if val == 'patFuncTitle':
                    self.inTitle = True
                    self.save_bgn()
                if val == 'patFuncStatus':
                    self.inStatus = True
                    self.save_bgn()

    #--------------------------------------------------------------------
    def end_td(self):
        if self.inTitle:
            self.inTitle = False
            self.title = self.save_end().strip()
        if self.inStatus:
            self.inStatus = False
            title = self.title
            daysUntilDue = parseStatus(self.save_end())
            self.title = None
            self.booksDue.append((title, daysUntilDue))

            

#------------------------------------------------------------------------
# The main body of the script.

for userName in [ "Michael", "Eileen", "Owen" ]:
    checkBooks(userName)
