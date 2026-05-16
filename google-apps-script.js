// ============================================================
//  KisanMart – Google Apps Script Backend
//  Paste this ENTIRE code into your Google Apps Script editor
//  (script.google.com → New Project → replace default code)
// ============================================================

const SHEET_ID = "1D2cX6hLLudhWDWCBqDAYbQQDvT6n1keC4JtDRuIEWNU"; // ← REPLACE THIS

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const type = data.type; // "order" | "rental" | "contact"

    const ss = SpreadsheetApp.openById(SHEET_ID);
    const timestamp = new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });

    if (type === "order") {
      saveOrder(ss, data, timestamp);
    } else if (type === "rental") {
      saveRental(ss, data, timestamp);
    } else if (type === "contact") {
      saveContact(ss, data, timestamp);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ status: "success" }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: "error", message: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Allow CORS preflight
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: "ok", message: "KisanMart API running" }))
    .setMimeType(ContentService.MimeType.JSON);
}

// ─── SAVE ORDER ───
function saveOrder(ss, data, timestamp) {
  let sheet = ss.getSheetByName("Orders");
  if (!sheet) {
    sheet = ss.insertSheet("Orders");
    sheet.appendRow([
      "Timestamp", "Order ID", "Customer Name", "Mobile", "Email",
      "Delivery Address", "Payment Method", "Items Ordered", "Notes", "Status"
    ]);
    // Style header row
    sheet.getRange(1, 1, 1, 10).setBackground("#1b5e20").setFontColor("#ffffff").setFontWeight("bold");
    sheet.setFrozenRows(1);
  }
  sheet.appendRow([
    timestamp,
    data.orderId,
    data.name,
    data.phone,
    data.email || "—",
    data.address,
    data.payment,
    data.items,
    data.notes || "—",
    "New Order 🆕"
  ]);
}

// ─── SAVE RENTAL ───
function saveRental(ss, data, timestamp) {
  let sheet = ss.getSheetByName("Rentals");
  if (!sheet) {
    sheet = ss.insertSheet("Rentals");
    sheet.appendRow([
      "Timestamp", "Booking ID", "Customer Name", "Mobile", "Village / District",
      "Equipment", "Rental Date", "Time Slot", "Duration", "Rate Per Day", "Notes", "Status"
    ]);
    sheet.getRange(1, 1, 1, 12).setBackground("#e65100").setFontColor("#ffffff").setFontWeight("bold");
    sheet.setFrozenRows(1);
  }
  sheet.appendRow([
    timestamp,
    data.bookingId,
    data.name,
    data.phone,
    data.location,
    data.equipment,
    data.date,
    data.slot,
    data.duration,
    data.rate,
    data.notes || "—",
    "Pending Confirmation 🕐"
  ]);
}

// ─── SAVE CONTACT QUERY ───
function saveContact(ss, data, timestamp) {
  let sheet = ss.getSheetByName("Contact Queries");
  if (!sheet) {
    sheet = ss.insertSheet("Contact Queries");
    sheet.appendRow([
      "Timestamp", "Name", "Mobile", "Email", "Query Type", "Message", "Status"
    ]);
    sheet.getRange(1, 1, 1, 7).setBackground("#1565c0").setFontColor("#ffffff").setFontWeight("bold");
    sheet.setFrozenRows(1);
  }
  sheet.appendRow([
    timestamp,
    data.name,
    data.phone,
    data.email,
    data.subject,
    data.message,
    "Unread 📬"
  ]);
}