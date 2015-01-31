# acccountBalance
#
# Functions to read a Quicken report file containing an account balance report.

from decimal import Decimal
import datetime
import re
import shutil
import smtplib
import sys

#-------------------------------------------------------------------
def read(fileName):
    '''Reads a report from a Quicken report plain text file.'''

    balanceDict = {}

    lines = iter(open(fileName, 'rb').read().strip().split('\n'))

    # Find the start of the Cash Accounts section.
    for line in lines:
        if line.strip() == 'Cash Accounts':
            break

    # Read the Cash Accounts section.
    for line in lines:

        # Check for the end of the section.
        if line.strip().startswith('TOTAL Cash Accounts'):
            break

        line = line.strip()
        if line:
            name, amount = line.rsplit(None, 1)
            balanceDict[name] = amount

    # Convert amounts from string to decimal.
    for key in balanceDict:
        amount = balanceDict[key]

        # Remove commas.
        amount = ''.join(amount.split(','))

        balanceDict[key] = Decimal(amount)

    # Flip the sign to creat an amount remaining, rather than an amount spent.
    for key in balanceDict:
        balanceDict[key] = -balanceDict[key]


    return balanceDict

#-------------------------------------------------------------------
def formatHtml(balanceDict):
    '''Write an HTML file with a list of balances.'''

    dateStr = datetime.date.today().strftime("%b %d, %Y")

    ret = '<html>\n'
    ret += '<head>\n'
    ret += '<title>Current Envelope Balances</title>\n'
    ret += '</head>\n'
    ret += '<body>\n'
    ret += '<h1>Current Envelope Balances</h1>\n'
    ret += '<h2>Generated: ' + dateStr + '</h2>\n'
    ret += '<table border="1">\n'
    ret += '<tr><td><b>Envelope</b></td><td><b>Amount</b></td></tr>\n'

    for key in sorted(balanceDict.keys()):
        name = key
        amount = balanceDict[key]

        if amount < 0:
            amountStr = '<font color="red">' + str(amount) + '</font>'
        else:
            amountStr = str(amount)

        ret += '<tr><td>' + name + '</td>'
        ret += '<td align="right">' + amountStr + '</td></tr>\n'
        
    ret += '</table>\n'
    ret += '</body>\n'
    ret += '</html>\n'

    return ret


#------------------------------------------------------------------------
def sendEmail(mailTos, balanceDict):
    """Sends a budget report email."""

    # The categories to include in the email.
    includeRes = [ 'Clothing.*',
                   'Dining.*',
                   'Groceries',
                   'Groceries Party',
                   'Household',
                   'Household Decoration' ]

    dateStr = datetime.date.today().strftime("%b %d, %Y")

    mailSubject = "Budget Envelope Report " + dateStr

    body = ''
    body += 'Current Envelope Balances\n'
    body += 'Generated: ' + dateStr + '\n'
    body += '\n'

    for key in sorted(balanceDict.keys()):
        for includeRe in includeRes:
            if re.match(includeRe + '$', key):
                body += "%-20s %9s\n" % (key, balanceDict[key])

    for mailTo in mailTos:
        sendGmail(mailTo, mailSubject, body)

#------------------------------------------------------------------------
def sendGmail(mailTo, mailSubject, mailBody):
    """Sends an email to the specified address with the specified message.

    @param mailTo The address to send the email to.
    @param mailSubject The subject of the email.
    @param mailBody The body of the email.
    """
    
    smtpServer = "smtp.gmail.com"
    #smtpPort = 465
    smtpPort = 587
    smtpUserName = "Michael.Philip.Brady@gmail.com"
    smtpPassword = "Naz3#gul"

    mailFrom =  "Michael.Philip.Brady@gmail.com"

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

#-------------------------------------------------------------------
def process(inFile, outFile, mailTos):
    '''Convert a Quicken text report to HTML.'''

    balanceDict = read(inFile)
    html = formatHtml(balanceDict)
    open(outFile, 'w').write(html)

    # Copy to Eileen's machine.
    shutil.copy(outFile, 'W:/')

    sendEmail(mailTos, balanceDict)

#-------------------------------------------------------------------
def test():

    inFile = 'C:/Users/mbrady/Documents/mbrady/quicken/accountBalances.txt'
    balanceDict = read(inFile)

    #print len(balanceDict)
    #for key in sorted(balanceDict.keys()):
    #    print key
    #    print balanceDict[key]

    html = formatHtml(balanceDict)
    print html

#-------------------------------------------------------------------
if __name__ == '__main__':
    
  args = sys.argv[1:]

  if len(args) == 0:
    inFile = 'C:/Users/mbrady/Documents/mbrady/quicken/accountBalances.txt'
    outFile = 'C:/Users/mbrady/Documents/mbrady/quicken/envelopeReport.html'

    mailTos = [ 'Michael.Philip.Brady@gmail.com', 'eileenbrady98@gmail.com ' ]

    process(inFile, outFile, mailTos)

  else:
    print """Usage:  report

Creates an envelope current balance report.
"""
    sys.exit( 1 )
