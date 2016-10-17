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
# A list of addresses to receive emails.
userEmails = ('Michael.Philip.Brady@gmail.com',
              #'4013384407@tmomail.net',                  
              'eileenbrady98@gmail.com',
              '4013384401@tmomail.net',              
              'acatani@gmail.com',
              )

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
     
        id, startEnd, workerTitle, workerLastName, school = extractInfo(job)
        ret.append((id, startEnd, workerTitle, workerLastName, school))

    return ret

#------------------------------------------------------------------------
def extractInfo(jobDict):
    '''Extracts info about a single job from a dictionary.
    '''

    workerTitle = "unknown"
    workerLastName = "unknown"
    school = "unknown"
    startEnd = "unknown"

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

          start = extractDate(item, 'Start')
          end = extractDate(item, 'End')

          if start:
              startEnd = start
          if end and start != end:
              startEnd += "-" + end

    return id, startEnd, workerTitle, workerLastName, school

#------------------------------------------------------------------------
def extractDate(itemDict, key):
    '''Extracts a single date value from a dictionary.
    '''

    value = None

    if key in itemDict:
        value = itemDict[key]

        # Parse just the date from the dateTtime ISO string.
        if 'T' in value:
            value = value.split('T')[0]

        value = value.replace('-', '/')

    return value

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
    mailSubject = "New Sub Job"

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

    # Load the list of jobs we've seen before.

    pickleFile = 'c:/Users/mbrady/Documents/checkSubstituteSeenIds.txt'

    seenIds = []
    if os.path.exists(pickleFile):
        seenIds = pickle.load(open(pickleFile, 'r'))

    # Read the list of jobs from the web page.

    thePage = readJobsPage()
    jobs = parse(thePage)

    #jobs.append(('sampleId', 'sampleName', 'sampleTitle', 'sampleSchool'))

    # Jobs we've never seen before.
    newJobs = []

    for jobTuple in jobs:
        id = jobTuple[0]
        
        if id not in seenIds:
            newJobs.append(jobTuple)
            seenIds.append(id)

    # Save the updated list of jobs we've seen.

    pickle.dump(seenIds, open(pickleFile, 'w'))

    #print 'SEEN IDS'
    #print seenIds

    #print 'NEW JOBS'
    #print newJobs    

    if newJobs:
    
        mailMsg = "New Jobs on Aseop:\n"

        for id, startEnd, workerTitle, workerLastName, school in newJobs:

            mailMsg += "----------------\n"
            mailMsg += ("%s %s %s %s\n" %
                        (startEnd, workerTitle, workerLastName, school))

        for userEmail in userEmails:
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

        emails = ('Michael.Philip.Brady@gmail.com',
                  'eileenbrady98@gmail.com')
        for userEmail in emails:
            sendGmail(userEmail, msg)

#------------------------------------------------------------------------
# The main body of the script.

checkJobs()
