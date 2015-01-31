

var SchwabReader = {};

// The column indexes in the HTML page.

var QS_POST_DATE_INDEX = 0;
var QS_TRANSACTION_DATE_INDEX = 1;
var QS_DESCRIPTION_INDEX = 2;
var QS_REF_NUMBER_INDEX = 4;
var QS_AMOUNT_INDEX = 5;

/** Parse a recent activity statement, returning the current balance and date.
 *
 * Call this when the current page contains a Schwab "Current Balance:" item.
 *
 * A list of 2 objects (the date and amount) will be returned.
 */
SchwabReader.readCurrentBalance = function()
{
  // There doesn't seems to be a balance date on the page, so just
  // use the present date.
  var theDate = new Date();

  // The current balance is in a table with the following structure,
  // so we'll find the text "Current Balance" then walk the tree
  // to the value.

  // <div class="trans-acc-sec fl-lt">
  //   <h2 class="h2-bold-14 greenbg">Account summary</h2>
  //   <div class="summary-acct-row">
  //     <div class="accnt-summary-left fl-lt">Current balance:</div>
  //     <div class="fl-rt top-fix TL_NPI_L1">$404.12</div>
  //     <div class="clearboth"></div>
  //   </div>
  //   <div class="summary-acct-row">
  //      ..
  //   </div>

  console.error("HELLO");
  console.error("HELLO");
  console.error("HELLO");
  console.error("HELLO");
  console.error("HELLO");
  console.error("HELLO");
  console.error("HELLO");
  console.error("HELLO");
  console.error("DOCUMENT", content.document);
  var currentBalanceNode = qsFindTextNode("Current Balance:");
console.error('node', currentBalanceNode);
  var row = currentBalanceNode.parentNode.parentNode;
console.error('row', row);

  // The div is the 2nd child, but we have to use index 4 because
  // the whitespace and comments between elements counts.
  var div = tr.childNodes[4];
console.error('div', div);
  var amountNode = div.childNodes[0];
console.error('amountNode', amountNode);
  var amountStr = amountNode.data;
console.error('amountStr', amountStr);

  // Remove the dollar sign.
  amountStr = amountStr.slice(1);

  // Normalize a credit
  // by removing the trailing CR and making it negative instead.
  var spaceIdx = amountStr.indexOf(" ");
  if (spaceIdx > -1) {
    amountStr = amountStr.slice(0, spaceIdx);
    amountStr = "-" + amountStr;
  }

  return [theDate, amountStr];
}

/** Parse a recent activity statement, returning the data as a list of maps.
 *
 * Call this when the current page contains a Schwab "Recent Activity" table.
 *
 * A list of objects, one per statement row, will be returned.
 */
SchwabReader.readTransactions = function()
{
  var table = qsFindElem('table', 'class', 'acctregistermodule');
  var trList = table.getElementsByTagName("TR");

  var vals = qsRowsToLists(trList);

  qsSplitTransactions(vals);

  vals = qsRowListsToMaps(vals);

  return vals;
}

/** Splits the 'Description' column into a 'name' and 'memo' items.
 */
function qsSplitTransactions(rowTextLists)
{
  var dashSep = "                         - ";

  for (var i = 0; i < rowTextLists.length; ++i) {
    var rowTextList = rowTextLists[i];
    var desc = rowTextList[QS_DESCRIPTION_INDEX];

    var splitTransaction = desc.split(dashSep);

    // Occasionally, there will be no seperator and no memo.
    // Set the memo to the empty string.
    if (splitTransaction.length == 1) {
      splitTransaction.push("");
    }

    // Normalize the payment name.
    if (splitTransaction.length >= 1 &&
        splitTransaction[0] == "PAYMENT - THANK YOU" ||
        splitTransaction[0] == "PENDING PAYMENT") {
      splitTransaction = [ "Payment", "" ];
    }

    if (splitTransaction.length != 2) {
      var msg = "Expected 2 transaction rows, but got " +
        splitTransaction.length + ".  Transaction text: '" + 
        rowTextList[QS_DESCRIPTION_INDEX] +
        "'";
      throw new Error(msg);
    }

    splitTransaction[0] = qsStringTrim(splitTransaction[0]);
    splitTransaction[1] = qsStringTrim(splitTransaction[1]);

    // Remove the old transaction and insert the 2 split ones.
    rowTextList.splice(QS_DESCRIPTION_INDEX, 
                       1,
                       splitTransaction[0],
                       splitTransaction[1]);
  }
}

/** Give a list of row lists, returns a list of row maps.
 */
function qsRowListsToMaps(listOfLists)
{
  var listOfMaps = [];

  for (var i = 0; i < listOfLists.length; ++i) {
    var rowList = listOfLists[i];

    var rowMap = {};

    // Have to add 1 to the indexes for items to the right of
    // the description which gets split.

    rowMap['name'] = rowList[QS_DESCRIPTION_INDEX];
    rowMap['memo'] = rowList[QS_DESCRIPTION_INDEX + 1];
    rowMap['postDate'] = rowList[QS_POST_DATE_INDEX];
    rowMap['transactionDate'] = rowList[QS_TRANSACTION_DATE_INDEX];
    rowMap['refNumber'] = rowList[QS_REF_NUMBER_INDEX + 1];
    rowMap['amount'] = rowList[QS_AMOUNT_INDEX + 1];
    
    listOfMaps.push(rowMap);
  }

  return listOfMaps;
}

/** Given a list of TR elements, returns a list of lists of TD text values.
 */
function qsRowsToLists(trList)
{
  var ret = [];

  // Skip the header row.
  // It has HTML within the text labels, so it's harder to parse.

  for (var i = 1; i < trList.length; ++i) {
    var tr = trList[i];

    // First row has header TH element, others have TD.
    var tdTagName = ((i == 0) ? "th" : "td");

    var tdList = tr.getElementsByTagName(tdTagName);

    qsAssert(tdList.length == 6, "TR row didn't have 6 TDs");

    if (qsIsGarbageRow(tdList)) {
      continue;
    }

    var tdValList = [];
    ret.push(tdValList);

    for (var j = 0; j < tdList.length; ++j) {
      var td = tdList[j];

      if (td.childNodes.length == 0) {
        var text = "";
      } else if (td.childNodes.length == 1) {
        var text = qsStringTrim(td.childNodes[0].nodeValue);
      } else {
        var msg = "Row " + i + ", col " + j + " has " + td.childNodes.length +
          " childNodes.";
        throw new Error(msg);
      }

      tdValList.push(text);
    }
  }
  return ret;
}

/** Returns true if the tr row is not a credit card transaction.
 */
function qsIsGarbageRow(tdList)
{
  var descIdx = QS_DESCRIPTION_INDEX;

  // Check for "Temporary Authorizations" row.

  var targetLabel = "Temporary Authorizations";
  if (tdList.length > descIdx &&
      tdList[descIdx].childNodes.length == 2 &&
      qsStringTrim(tdList[descIdx].childNodes[1].nodeValue) == targetLabel) {

    return true;
  }

  // Check for "Purchases and Adjustments" row.

  var targetLabel = "Purchases and Adjustments";
  if (tdList.length > descIdx &&
      tdList[descIdx].childNodes.length == 1 &&
      qsStringTrim(tdList[descIdx].childNodes[0].nodeValue) == targetLabel) {

    return true;
  }

  // Check for a blank row.

  var isBlank = true;
  for (var i = 0; i < tdList.length; ++i) {
    var tdItem = tdList[i];
    var childNodes = tdItem.childNodes;
    
    if (childNodes.length != 1 || qsStringTrim(childNodes[0].nodeValue) != '') {
      isBlank = false;
      break;
    }
  }
  if (isBlank) {
    return true;
  }

  return false;
}
