import re
import frappe
from frappe.model.document import Document


def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[\"']", "", text)            # remove quotes
    text = re.sub(r"[^a-z0-9]+", "-", text)      # non-alphanum -> hyphen
    text = re.sub(r"-+", "-", text)              # collapse hyphens
    text = text.strip("-")
    return text


class Category(Document):
    def validate(self):
        self._inherit_section_from_parent()
        self._set_slug()
        self._prevent_duplicate_in_same_parent()

    def _inherit_section_from_parent(self):
        if not self.parent_category:
            return

        parent_section = frappe.db.get_value("Category", self.parent_category, "section")
        if parent_section:
            self.section = parent_section

    def _set_slug(self):
        # Always slug from title only (simple + consistent)
        self.slug = slugify(self.title)

        if not self.slug:
            frappe.throw("Slug cannot be empty. Please set a valid Title.")

    def _prevent_duplicate_in_same_parent(self):
        # Prevent duplicates *within same parent*
        # (so under Docs you cannot create two 'getting-started')
        filters = {
            "slug": self.slug,
            "parent_category": self.parent_category or "",
            "name": ["!=", self.name],
        }

        exists = frappe.db.exists("Category", filters)
        if exists:
            parent = self.parent_category or "(root)"
            frappe.throw(f"Duplicate category slug '{self.slug}' under parent {parent} is not allowed.")
