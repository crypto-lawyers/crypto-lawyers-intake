// GOOGLE APPS SCRIPT - Copy this into your Google Sheet
// Go to: Extensions > Apps Script > Paste this code > Deploy

function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    // Add timestamp and case reference
    var row = [
      new Date(),                              // Timestamp
      "WB156-26",                             // Case Reference
      data.full_name || "",                    // Full Name
      data.entity_name || "",                  // Entity
      data.email || "",                        // Email
      data.phone || "",                        // Phone
      data.address || "",                      // Address
      data.country || "",                      // Country
      data.contact_preference || "",           // Contact Preference
      data.initial_contact || "",              // Initial Contact Method
      data.referral_type || "",                // Referral Type
      data.platform_clone || "",               // Platform Clone
      data.fake_urls || "",                    // Fake URLs
      data.fake_app_name || "",                // Fake App Name
      data.fake_profits || "",                 // Fake Profits
      data.scam_timeline || "",                // Scam Timeline
      data.loss_tier || "",                    // Loss Tier
      data.loss_dates || "",                   // Loss Dates
      data.total_loss || "",                   // Total Loss
      data.transfer_count || "",               // Transfer Count
      (data.crypto_type || []).join(", "),     // Crypto Types
      data.financial_source || "",             // Financial Source
      data.wallet_addresses || "",             // Wallet Addresses
      data.transaction_hashes || "",           // Transaction Hashes
      data.source_wallet || "",                // Source Wallet
      data.other_wallet || "",                 // Other Wallet
      data.multiple_addresses || "",           // Multiple Addresses
      (data.evidence || []).join(", "),        // Evidence Types
      data.can_provide_docs || "",             // Can Provide Docs
      data.law_enforcement_report || "",       // Law Enforcement Report
      data.police_report_number || "",         // Police Report Number
      data.consent_accuracy || "",             // Consent Accuracy
      data.consent_review || "",               // Consent Review
      data.consent_contact || "",              // Consent Contact
      data.consent_no_relationship || "",      // Consent No Relationship
      data.consent_data_sharing || ""          // Consent Data Sharing
    ];
    
    sheet.appendRow(row);
    
    return ContentService
      .createTextOutput(JSON.stringify({status: "success"}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({status: "error", message: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({status: "running"}))
    .setMimeType(ContentService.MimeType.JSON);
}
