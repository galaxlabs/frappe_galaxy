import re
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class GalaxyContent(Document):
    pass



# _slug_rx = re.compile(r"[^a-z0-9-]+")

# def slugify(txt: str) -> str:
#     s = (txt or "").strip().lower().replace(" ", "-")
#     s = _slug_rx.sub("-", s)
#     s = re.sub(r"-{2,}", "-", s).strip("-")
#     return s or "page"

# class GalaxyContent(Document):
#     def before_validate(self):
#         # always normalize slug (even if user typed it manually)
#         if self.title and not self.slug:
#             self.slug = slugify(self.title)
#         else:
#             self.slug = slugify(self.slug)

#         # ✅ make /g/<slug> the canonical route
#         self.route = f"g/{self.slug}"

#         # publish bookkeeping
#         if self.status == "Published" and not self.published_on:
#             self.published_on = now_datetime()

#         # ✅ is_published_field must be a Check field
#         self.published = 1 if (self.status == "Published" and self.is_public) else 0

#         # meta defaults
#         if not self.meta_title:
#             self.meta_title = self.title
#         if not self.meta_description and self.summary:
#             self.meta_description = (self.summary or "")[:160]


# # Copyright (c) 2025, Galaxy Labs and contributors
# # For license information, please see license.txt

# import re
# import frappe
# from frappe.model.document import Document
# from frappe.utils import now_datetime

# _slug_rx = re.compile(r"[^a-z0-9-]+")

# def slugify(txt: str) -> str:
#     s = (txt or "").strip().lower().replace(" ", "-")
#     s = _slug_rx.sub("-", s)
#     s = re.sub(r"-{2,}", "-", s).strip("-")
#     return s or "page"

# TYPE_PREFIX = {
#     "Doc": "docs",
#     "Tutorial": "tutorials",
#     "Wiki": "wiki",
#     "Note": "notes",
#     "Profile": "profiles",
# }

# class GalaxyContent(Document):
#     def before_validate(self):
#         if not self.slug and self.title:
#             self.slug = slugify(self.title)

#         prefix = TYPE_PREFIX.get(self.content_type, "g")
#         self.route = f"{prefix}/{self.slug}"

#         # meta defaults
#         if not self.meta_title:
#             self.meta_title = self.title
#         if not self.meta_description and self.summary:
#             self.meta_description = (self.summary or "")[:160]

#     def validate(self):
#         # publish date
#         if self.status == "Published" and not self.published_on:
#             self.published_on = now_datetime()
