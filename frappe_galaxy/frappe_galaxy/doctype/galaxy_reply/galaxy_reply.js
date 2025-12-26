// Copyright (c) 2025, Galaxy Labs and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Galaxy Reply", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Galaxy Reply", {
  refresh(frm) {
    frm.add_custom_button("✅ Mark as Solution", async () => {
      await frappe.call("frappe_galaxy.api.mark_solution", {
        reply: frm.doc.name
      });
      frm.reload_doc();
    });
  }
});
