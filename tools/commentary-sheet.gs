// Google Apps Script for the Hiraya commentary sheet.
// Paste into Extensions, Apps Script, inside a Google Sheet. Deploy as a Web app:
// Execute as: Me. Who has access: Anyone. Copy the Web app URL into summary.html, Set up saving.
var TAB = 'Commentary';
function tab_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) throw new Error('Script is not attached to a sheet. Create it from Extensions, Apps Script inside the sheet.');
  var sh = ss.getSheetByName(TAB);
  if (!sh) { sh = ss.insertSheet(TAB); sh.appendRow(['Key', 'Pages', 'Title', 'Commentary', 'Updated']); sh.setFrozenRows(1); }
  return sh;
}
function doPost(e) {
  try {
  var d = JSON.parse(e.postData.contents), sh = tab_();
  var lock = LockService.getScriptLock(); lock.waitLock(10000);
  (d.groups || []).forEach(function (g) {
    var rows = sh.getDataRange().getValues(), at = 0;
    for (var i = 1; i < rows.length; i++) { if (rows[i][0] === g.key) { at = i + 1; break; } }
    var vals = [[g.key, g.pages, g.title, g.text, g.updated]];
    if (at) sh.getRange(at, 1, 1, 5).setValues(vals); else sh.appendRow(vals[0]);
  });
  lock.releaseLock();
  return ContentService.createTextOutput('ok');
  } catch (err) { return ContentService.createTextOutput('error: ' + err); }
}
function doGet() {
  var rows = tab_().getDataRange().getValues(), out = {};
  for (var i = 1; i < rows.length; i++) out[rows[i][0]] = { pages: rows[i][1], title: rows[i][2], text: rows[i][3], updated: String(rows[i][4]) };
  return ContentService.createTextOutput(JSON.stringify({ groups: out })).setMimeType(ContentService.MimeType.JSON);
}
