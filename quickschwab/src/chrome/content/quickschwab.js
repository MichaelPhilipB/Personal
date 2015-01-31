// quickschwab.js
//
// The main file for the quickschwab extension.

/** Initialize this extension.
 */
function qsInit()
{
console.error("quInit foo foo foo");
  window.addEventListener("load", qsWindowLoaded, false);
}

/** Called when a window has loaded.
 */
function qsWindowLoaded()
{
  var appcontent = document.getElementById("appcontent");
  if(appcontent) {
    appcontent.addEventListener("DOMContentLoaded", qsDomContentLoaded, true);
  }
}

/** Called when a new page has loaded.
 */
function qsDomContentLoaded(aEvent)
{
  // Document that triggered the event.
  var doc = aEvent.originalTarget;
  console.error('qsDom loaded', doc.location.href, doc.location.href.search("target=acctdetails"));

  // If this page is a Credit Card page, add the download button
  // and button click event handler.
  if(doc.location.href.search("target=acctdetails") > -1) {
    qsAddDownloadButton(doc);
    doc.addEventListener("qsDownloadClicked", qsRun, false);
  }
}

/** Adds a 'Download' button to the page.
 */
function qsAddDownloadButton(doc)
{
  // Add a button whose onclick will start the download.
  var button = doc.createElement("input");
  button.type = "button";
  button.value = "Download QFX";

  // I tried a million ways to set up 'onclick' to call a function.
  // button.setAttribute(String, String) was the only one that worked.
  // button.setAttribute(String, function) doesn't work!

  // The web page javascript isn't allowed to see the extension
  // javascript, so we can't just call extensions functions directly.
  // We have to fire an event that the extension can listen for.
  var code =
    "var evt = document.createEvent('Events');"  +
    "evt.initEvent('qsDownloadClicked', true, true);" +
    "document.dispatchEvent(evt);";
  button.setAttribute("onclick", code);

  // Insert the button into the page.
  //
  // Under div class=fsdav-topnav is the ul class=fsdnav-nav-list we want.

  var ul = qsFindElem("ul", "class", "fsdnav-nav-list");
  var firstLi = ul.childNodes[0];
  var newLi = doc.createElement("li");
  newLi.appendChild(button);
  ul.insertBefore(newLi, firstLi);
}

/** Break up the file name into a directory and file-only name.
 *
 *  The dir name should end with a trailing slash.
 */
function qsParseFilePath(filePath)
{
  var forwardIndex = filePath.lastIndexOf("/");
  var backIndex = filePath.lastIndexOf("\\");
  var slashIndex = forwardIndex > backIndex ? forwardIndex : backIndex;

  if (slashIndex < 0) {
    var dirName = "";
    var fileName = filePath;
  } else if (slashIndex + 1 == filePath.length) {
    var msg =
      "Filename '" + filePath + "' " +
      "is invalid.  Please go to the quickschwab options panel and enter " +
      "a valid save file name.";
    throw new Error(msg);
  } else {
    // Put a trailing slash on the dir name.
    var dirName = filePath.substring(0, slashIndex + 1);
    var fileName = filePath.substring(slashIndex + 1);
  }

  var dir = DirIO.open(dirName);
  if(!dir || !dir.exists()) {
    var msg =
      "Directory '" + dirName + "' " +
      "is invalid.  Please go to the quickschwab options panel and enter " +
      "a valid save file name.";
    throw new Error(msg);
  }

  var ret = { "dir" : dirName, "file" : fileName };
  return ret;
}

/** Executes a QFX download.
 */
function qsRun()
{
  try {
    qsWriteAndLaunch();
  } catch (e) {
    alert("Quickschwab extension error: " + e);
    console.error('Quickschwab exception', e);
  }
}

/** Executes a QFX download.
 */
function qsWriteAndLaunch()
{
  // Read the file name preference.
  var classes = Components.classes["@mozilla.org/preferences-service;1"];
  var prefs = classes.getService(Components.interfaces.nsIPrefBranch);
  var savePath = prefs.getCharPref("extensions.quickschwab.savefile");
  var acctNum = prefs.getCharPref("extensions.quickschwab.acctnum");

  // Break up the file name into a directory and file-only name.
  var dirFile = qsParseFilePath(savePath);
  if (dirFile == null) {
    return;
  } else {
    var saveDir = dirFile.dir;
    var saveFile = dirFile.file;
  }

  // Read the page.

  var dateBalance = SchwabReader.readCurrentBalance();
  var dateAsOf = dateBalance[0];
  var balance = dateBalance[1];

  var rowList = SchwabReader.readTransactions();

  // Write a .qfx file.

  QfxWriter.write(saveDir, saveFile, acctNum, rowList, balance, dateAsOf);

  // Launch the .qfx file to get it into Quicken.

  var classes = Components.classes["@mozilla.org/file/local;1"];
  var file = classes.createInstance(Components.interfaces.nsILocalFile);

  file.initWithPath(savePath);

  // Launching is like double-clicking on the file's icon.
  file.launch();
}
