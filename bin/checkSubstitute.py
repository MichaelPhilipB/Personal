#------------------------------------------------------------------------
# checkSubstitute.py
#
# Queries the Barrington substitute teacher web page.
# If there are new jobs, sends an email.
#------------------------------------------------------------------------

import os
import json
import pickle
import cookielib
import copy
import datetime
import formatter
import htmllib
import os
import smtplib
import sys
import traceback
import urllib
import urllib2

#------------------------------------------------------------------------
# A dictionary of names to email.
#users = {
#    "Michael" : ("Michael.Philip.Brady@gmail.com"),
#    "Eileen"  : ("eileenbrady98@gmail.com"),
#    }

#------------------------------------------------------------------------
def parse(text):
    '''Parses the Aseop web page that lists jobs, returning a list of jobs.
    '''

    # There's a chunk of almost-JSON in the middle of the page that lists
    # the jobs.  Find it.
    beginIndex = text.index('var pageVars = {')
    endIndex = text.index('};', beginIndex)
    
    chunk = text[beginIndex + len('var pageVars = '): endIndex + 1]


    # This is Javascript, not JSON, so turn it into valid JSON.
    chunk = chunk.replace('curJobs:', '"curJobs":')
    chunk = chunk.replace('availJobs:', '"availJobs":')
    chunk = chunk.replace('nwds:', '"nwds":')
    chunk = chunk.replace('tenants:', '"tenants":')
    chunk = chunk.replace('startDate:', '"startDate":')
    chunk = chunk.replace('endDate:', '"endDate":')
    chunk = chunk.replace('historyDays:', '"historyDays":')

    # Extract out the one line we care about, and parse it.

    lines = chunk.split('\n')
    line = lines[2]
    line = line.strip()[:-1]

    obj = json.loads('{' + line + '}')


    availJobs = obj['availJobs']
    jobList = availJobs['list']

    ret = []
    for job in jobList:
     
        id, workerTitle, workerLastName, school = extractInfo(job)
        ret.append((id, workerTitle, workerLastName, school))

    return ret

#------------------------------------------------------------------------
def extractInfo(jobDict):
    '''Extracts info about a single job from a dictionary.
    '''

    workerTitle = "unknown"
    workerLastName = "unknown"
    school = "unknown"

    if 'Id' not in jobDict:
        raise Exception("No ID in job dict: " + str(jobDict))

    id = jobDict['Id']
    if 'WorkerTitle' in jobDict:
      workerTitle = jobDict['WorkerTitle']
    if 'WorkerLastName' in jobDict:
      workerLastName = jobDict['WorkerLastName']

    if 'Items' in jobDict:
      items = jobDict['Items']

      if items:
          item = items[0]
          if 'Institution' in item:
              institution = item['Institution']
              if 'Name' in institution:
                  school = institution['Name']

    return id, workerTitle, workerLastName, school

#------------------------------------------------------------------------
def readJobsPage():
    """Reads the web site, returns the HTML page listing jobs.

    @return The HTML string of the checked out books page.
    """

    # Set up urllib2 to handle cookies.
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor()) 
    urllib2.install_opener(opener)

    # Log in.
    
    url = 'https://www.aesoponline.com/login.asp'

    #print 'DOWNLOAD JOBS PAGE'
    # Download the log in page.  We won't use this for anything,
    # but it gets the session cookies set up.
    #req = urllib2.Request(url)
    #urllib2.urlopen(req)

    # Post the log in form.
    values = {'id' : '4013384401',
              'pinPlain' : 'PIN',
              'pin' : '10240',
              'submit' : '1'}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)

    responseText = response.read()

    return responseText

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
    smtpPassword = "Naz3#gul"

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
def readAndSendEmail():
    """Reads the web page and sends an email for the specified user.
    """

    thePage = readJobsPage()
    
    pickleFile = 'c:/Users/mbrady/Documents/checkSubstituteSeenIds.txt'

    seenIds = []
    if os.path.exists(pickleFile):
        seenIds = pickle.load(open(pickleFile, 'r'))

    #text = open('aseopHome.htm').read()

    jobs = parse(thePage)

    newJobs = []
    for jobTuple in jobs:
        id = jobTuple[0]
        print seenIds, id, id in seenIds
        
        if id not in seenIds:
            newJobs.append(jobTuple)
            seenIds.append(id)

    print 'SEEN IDS'
    print seenIds
    pickle.dump(seenIds, open(pickleFile, 'w'))

    print 'NEW JOBS'
    print newJobs    

    if False and newJobs:
    
        mailMsg = "New Jobs on Aseop:\n"
        #mailMsg += "https://catalog.oslri.net/patroninfo\n"

        for id, workerTitle, workerLastName, school in newJobs:

            mailMsg += "----------------\n"
            mailMsg += ("%s %s %s %s\n" %
                        (id, workerTitle, workerLastName, school))

        emails = ('Michael.Philip.Brady@gmail.com',
                  'eileenbrady98@gmail.com')
        for userEmail in emails:
            sendGmail(userEmail, mailMsg)

#------------------------------------------------------------------------
def checkJobs():
    """The main function that should be called.
    """

    try:
        readAndSendEmail()
    except Exception, e:
        msg = "An error occured while checking sub jobs.  "
        msg += "Please tell Michael about this.\n\n"
        msg += "Error:\n"

        excMsgLines = traceback.format_exception(*sys.exc_info())
        excMsg = "".join(excMsgLines)
        msg += excMsg

        # TODO remove
        raise e
        emails = ('Michael.Philip.Brady@gmail.com',
                  'eileenbrady98@gmail.com')
        for userEmail in emails:
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

checkJobs()

