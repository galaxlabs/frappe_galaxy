// Copyright (c) 2025, Galaxy Labs and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Category", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Category", {
  setup(frm) {
    frm.set_df_property("slug", "read_only", 1); // keep clean, auto-managed
  },

  refresh(frm) {
    toggle_section_lock(frm);
  },

  title(frm) {
    set_slug(frm);
  },

  section(frm) {
    // For top-level categories, section change should update slug
    set_slug(frm);
  },

  parent_category(frm) {
    if (!frm.doc.parent_category) {
      toggle_section_lock(frm);
      set_slug(frm);
      return;
    }

    // inherit section from parent
    frappe.db.get_value("Category", frm.doc.parent_category, ["section"], (r) => {
      if (r && r.section) frm.set_value("section", r.section);
      toggle_section_lock(frm);
      set_slug(frm);
    });
  }
});

function toggle_section_lock(frm) {
  const locked = !!frm.doc.parent_category; // lock section for child nodes
  frm.set_df_property("section", "read_only", locked);
}

function slugify(text) {
  return (text || "")
    .toString()
    .trim()
    .toLowerCase()
    .replace(/['"]/g, "")            // remove quotes
    .replace(/[^a-z0-9]+/g, "-")     // non-alphanum -> hyphen
    .replace(/-+/g, "-")             // collapse hyphens
    .replace(/^-|-$/g, "");          // trim hyphens
}

function set_slug(frm) {
  // Keep slug simple:
  // - Always slug from title only
  // (because your tree already separates Docs/Tutorials etc)
  const title = frm.doc.title || "";
  frm.set_value("slug", slugify(title));
}
