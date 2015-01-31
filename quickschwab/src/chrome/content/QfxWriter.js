


var QfxWriter = {};


/** Writes a .qfx file.
 */
QfxWriter.write = function(dirName,
                           fileName,
                           acctNum,
                           transactionList,
                           balanceAmt,
                           dateAsOf)
{
  var text = QfxWriter.createHeader(acctNum);

  for (var i = 0; i < transactionList.length; ++i) {
    var transaction = transactionList[i];

    //for (var j = 0; j < transaction.length; ++j) {
    //  qsConsole(j + ": " + transaction[j]);
    // }

    var name = transaction['name'];
    var memo = transaction['memo'];
    var postDateStr = transaction['postDate'];
    var transactionDate = transaction['transactionDate'];
    var refNumber = transaction['refNumber'];
    var amount = transaction['amount'];

    // Don't write TEMP transactions.  Wait for them to post.
    if (refNumber == "TEMP") {
      continue;
    }

    text += QfxWriter.makeTransaction(postDateStr, amount, name, refNumber);
  }

  text += QfxWriter.makeFooter(balanceAmt, dateAsOf);

  qsWriteFile(dirName, fileName, text);
}

/** Creates the QFX header.
 *
 * @param acctNum The account number to include in the header.
 */
QfxWriter.createHeader = function(acctNum)
{
var header =
"OFXHEADER:100\n" +
"DATA:OFXSGML\n" +
"VERSION:102\n" +
"SECURITY:NONE\n" +
"ENCODING:USASCII\n" +
"CHARSET:1252\n" +
"COMPRESSION:NONE\n" +
"OLDFILEUID:NONE\n" +
"NEWFILEUID:NONE\n" +
"\n" +
"<OFX>\n" +
"    <SIGNONMSGSRSV1>\n" +
"        <SONRS>\n" +
"            <STATUS>\n" +
"                <CODE>0\n" +
"                <SEVERITY>INFO\n" +
"            </STATUS>\n" +
"            <DTSERVER>20091030000000[-5:EST]\n" +
"            <LANGUAGE>ENG\n" +
"            <FI>\n" +
"                <ORG>FIA Card Services\n" +
"                <FID>5853\n" +
"            </FI>\n" +
"            <INTU.BID>5853\n" +
"        </SONRS>\n" +
"    </SIGNONMSGSRSV1>\n" +
"    <CREDITCARDMSGSRSV1>\n" +
"        <CCSTMTTRNRS>\n" +
"            <TRNUID>20091030000000[-5:EST]\n" +
"            <STATUS>\n" +
"                <CODE>0\n" +
"                <SEVERITY>INFO\n" +
"            </STATUS>\n" +
"            <CCSTMTRS>\n" +
"                <CURDEF>USD\n" +
"                <CCACCTFROM>\n" +
"                    <ACCTID>" + acctNum + "\n" +
"                </CCACCTFROM>\n" +
"                <BANKTRANLIST>\n" +
"                    <DTSTART>20091020040000[-5:EST]\n" +
"                    <DTEND>20091028040000[-5:EST]\n";

return header;
}


QfxWriter.makeTransaction = function(postDateStr, amount, name, refNumber)
{
  amount = QfxWriter.moneyToDecimal(amount);

  var isNegative = amount.length > 0 && amount.charAt(0) == '-';

  //qsConsole("amount.length > 0 ? " + amount.length > 0);
  //qsConsole("amount.charAt(0) - ? " + amount.charAt(0) == '-');
  //qsConsole("isNegative ? " + isNegative);

  // TODO see what Schwab calls a CREDIT.
  var transactionType = isNegative ? "PAYMENT" : "CREDIT";

  var dateFormatted = QfxWriter.fmtDate(postDateStr);
  var fitId = QfxWriter.fmtFitId(postDateStr, refNumber);

  var ret =  
"                    <STMTTRN>\n" +
"                        <TRNTYPE>" + transactionType + "\n" +
"                        <DTPOSTED>" + dateFormatted + "\n" +
"                        <TRNAMT>     " + amount + "\n" +
"                        <FITID>" + fitId + "\n" +
"                        <NAME>" + name + "\n" +
"                    </STMTTRN>\n";

  return ret;
}

/**
 *
 * balanceAmt The current balance.  Should be string.
 *            The number should be positive.
 * dateAsOf The current date.  Should be a date.js Date object.
 */
QfxWriter.makeFooter = function(balanceAmt, dateAsOf)
{
  balanceAmt = QfxWriter.moneyToDecimal(balanceAmt);
  var dateAsOfFormatted = dateAsOf.toString("yyyyMMdd"); 
  var footer =
"                </BANKTRANLIST>\n" +
"                <LEDGERBAL>\n" +
"                    <BALAMT>  " + balanceAmt + "\n" +
"                    <DTASOF>" + dateAsOfFormatted  + "\n" +
"                </LEDGERBAL>\n" +
"            </CCSTMTRS>\n" +
"        </CCSTMTTRNRS>\n" +
"    </CREDITCARDMSGSRSV1>\n" +
"</OFX>\n";

  return footer;
}


/** Formats a money string as a decimal.
 */
QfxWriter.moneyToDecimal = function(moneyStr)
{
  // Remove any commas from the balance string.
  moneyStr = moneyStr.replace(/,/g,'');

  // Remove a leading dollar sign.
  // There may also be a dollar sign after a negative sign.
  moneyStr = moneyStr.replace(/[$]/g,'');

  // Flip the sign.
  if (moneyStr.charAt(0) == '-') {
    moneyStr = moneyStr.slice(1);
  } else {
    moneyStr = "-" + moneyStr;
  }

  return moneyStr;
}

/** Formats a MM/DD/YYYY date as YYYYMMDD040000[-5:EST].
 */
QfxWriter.fmtDate = function(dateStr)
{
  var dateElems = dateStr.split("/");
  var year = dateElems[2];
  var month = dateElems[0];
  var day = dateElems[1];

  //var ret = year + month + day + "040000[-5:EST]";
  var ret = year + month + day;
  return ret;
}

/** Formats a MM/DD/YYYY post date and count as a FIT ID.
 */
QfxWriter.fmtFitId = function(postDateStr, refNumber)
{
  var dateElems = postDateStr.split("/");
  var year = dateElems[2];
  var month = dateElems[0];
  var day = dateElems[1];

  var ret = year + month + day + 'x' + refNumber;
  return ret;
}
