function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
    var data = JSON.parse(e.postData.contents);
    sheet.appendRow([
      new Date(),
      data.session_id || "",
      data.role || "",
      data.message || "",
      data.page_url || "",
      data.source || "",
      data.response_type || "",
      data.matched_intent || "",
      data.matched_aroma || "",
      data.matched_category || ""
    ]);
    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(error) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
