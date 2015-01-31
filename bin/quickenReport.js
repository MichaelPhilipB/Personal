// quickenReport.js
//
// Starts Quicken, saves report files, and exits Quicken.

///////////////////////////////////////////////////////////////////////
/** Sends a key stroke to a specified window.
 *
 * @param shell The WScript.Shell object to use.
 * @param windowTitle The title of the window to send the message to.
 *                    If 'null', the current active window will be used.
 * @param key The keystroke to send.
 */
function sendKey(shell, windowTitle, key)
{
  if (windowTitle) {
    shell.AppActivate(windowTitle);
    WScript.Sleep(100);
  }
  shell.SendKeys(key);
  WScript.Sleep(800);
}

///////////////////////////////////////////////////////////////////////
// The main body of the script.

var shell = WScript.CreateObject("WScript.Shell");

shell.run("\"C:\\Program Files (x86)\\Quicken\\qw.exe\"");
WScript.Sleep(100);


// Ctrl  ^
// Alt   %
// Shift +


// Save the monthly report.

// Bring up the Report window.
var window = "Quicken 2008 Deluxe - brady - [Quicken Home]";
sendKey(shell, window, "%r");
sendKey(shell, window, "{Down}");
sendKey(shell, window, "{Down}");
sendKey(shell, window, "{Right}");
sendKey(shell, window, "{Right}");
sendKey(shell, window, "{Enter}");

// Bring up the Save dialog.
window = null;
sendKey(shell, window, "%e");
sendKey(shell, window, "{Down}");
sendKey(shell, window, "{Enter}");

// Enter the Save file name.
window = null;
sendKey(shell, window, "monthToDateReport.txt");
sendKey(shell, window, "{Enter}");

// Confirm that we want to replace.
window = null;
sendKey(shell, window, "%y");

// Close the report window.
window = null;
sendKey(shell, window, "%{F4}");

// Save the annual report.

// Bring up the Report window.
window = "Quicken 2008 Deluxe - brady - [Quicken Home]";
sendKey(shell, window, "%r");
sendKey(shell, window, "{Down}");
sendKey(shell, window, "{Down}");
sendKey(shell, window, "{Right}");
sendKey(shell, window, "{Right}");
sendKey(shell, window, "{Down}");
sendKey(shell, window, "{Enter}");

// Bring up the Save dialog.
window = null;
sendKey(shell, window, "%e");
sendKey(shell, window, "{Down}");
sendKey(shell, window, "{Enter}");

// Enter the Save file name.
window = null;
sendKey(shell, window, "yearToDateReport.txt");
sendKey(shell, window, "{Enter}");

// Confirm that we want to replace.
window = null;
sendKey(shell, window, "%y");

// Close the report window.
window = null;
sendKey(shell, window, "%{F4}");

// Close the app.
window = "Quicken 2008 Deluxe - brady - [Quicken Home]";
sendKey(shell, window, "%{F4}");

// Qucken might ask if we want to backup or exit.
window = null;
sendKey(shell, window, "x");
