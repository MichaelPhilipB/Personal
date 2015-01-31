
function qsAssert(condition, msg)
{
  if (!condition) {

    var assertMsg = "Assertion failed";
    if (msg) {
      assertMsg += ": " + msg;
    }
    throw new Error(assertMsg);
  }
}

function qsConsole(msg)
{
  Components.utils.reportError(msg);
}

function qsStringTrim(s)
{
  return s.replace(/^\s*/, "").replace(/\s*$/, "");
}

function qsStringStartsWith(text, prefix)
{
  return text.indexOf(prefix) == 0;
}

/** Returns the text node that matches a given value.
 */
function qsFindTextNode(targetValue)
{
  console.warn('DOC DOC');
  console.warn(content.document.body); 
 return qsImplFindTextNode(content.document.body, targetValue, false);
}

/** Returns the text node that starts with a given value.
 */
function qsFindPrefixTextNode(targetValue)
{
  return qsImplFindTextNode(content.document, targetValue, true);
}

/** Implementation function for findTextNode.
 *
 * @param theParent The node whose children will be searched.
 * @param targetValue The text to search for.
 * @param prefixMatch Whether to search for prefix match or exact match.
 */
function qsImplFindTextNode(theParent, targetValue, prefixMatch)
{
  var msg = "" + theParent.nodeName;
  if (theParent.className)
    {
      msg += " " + theParent.className;
    }
  console.warn(msg);
  if (!theParent['childNodes']) {
    return null;
  }

  for (var i = 0; i < theParent.childNodes.length; ++i) {
    var childNode = theParent.childNodes[i];
    console.error(childNode.nodeType, childNode.className, childNode.data);
    if (childNode.nodeType == 3) {
      var text = childNode.data;
      if ((!prefixMatch && text == targetValue) ||
          (prefixMatch && qsStringStartsWith(text, targetValue))) {
        return childNode;
      }
    } else {
      var ret = qsImplFindTextNode(childNode, targetValue, prefixMatch);
      if (ret != null) {
        return ret;
      }
    }
  }
  return null;
}

function qsFindElem(tagName, attrName, attrValue)
{
  var allElems = content.document.getElementsByTagName(tagName);
  var theElem = null;
  for (var i = 0; i < allElems.length; i++) {
    if (allElems[i].getAttribute(attrName) == attrValue) {
      if (theElem != null) {
        var msg = "Error trying to find a node of type '" + tagName + "' " +
	  "with a(n) '" + attrName + "' with a value of '" + attrValue + "'. " +
	  "I expected to only find one node, but multiple nodes were found.";
	alert(msg);
	throw new Error(msg);
      } 
      theElem = allElems[i];
    }
  }
  return theElem;
}

function qsWriteFile(dirName, fileName, text)
{
  var dir = DirIO.open(dirName);
  if(!dir || !dir.exists()) 
  { 
    throw new Error("Failed to open write directory: " + dirName); 
  }  

  var file = dir;
  file.append(fileName);

  if (!file.exists())
  {
    if (!FileIO.create(file))
    {
      throw new Error("Failed to create file: " + fileName);
    }
  }
   
  if (!FileIO.write(file, text)) {
    throw new Error("Failed to write to file: " + fileName);
  }
}
