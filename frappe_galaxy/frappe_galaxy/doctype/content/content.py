import re
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils import now_datetime
from frappe.utils.data import strip_html

_slug_rx = re.compile(r"[^a-z0-9-]+")
_space_rx = re.compile(r"\s+")

TYPE_PREFIX = {
    "Doc": "docs",
    "Tutorial": "tutorials",
    "Wiki": "wiki",
    "Note": "notes",
    "Profile": "profiles",
    "Article": "articles",
    "HowTo": "howto",
    "FAQ": "faq",
    "Portfolio": "portfolio",
    "Jobs": "jobs",
    "Projects": "projects",
    "Post": "posts",
}

def slugify(txt: str) -> str:
    s = (txt or "").strip().lower()
    s = _space_rx.sub(" ", s).replace(" ", "-")
    s = _slug_rx.sub("-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "page"

def normalize_tags_csv(tags_csv: str) -> list[str]:
    if not tags_csv:
        return []
    out = []
    seen = set()
    for t in tags_csv.split(","):
        t = (t or "").strip().lower()
        t = re.sub(r"\s+", "-", t)
        t = re.sub(r"[^a-z0-9:\-]", "", t)
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out

def ensure_unique_slug(doc, prefix: str):
    """Ensure uniqueness of (content_type, slug) by adding -2, -3 suffix."""
    base = doc.slug
    if not base:
        base = "page"
    slug = base
    i = 2

    while True:
        exists = frappe.db.exists(
            "Content",
            {
                "content_type": doc.content_type,
                "slug": slug,
                "name": ["!=", doc.name or ""],
            },
        )
        if not exists:
            doc.slug = slug
            return
        slug = f"{base}-{i}"
        i += 1

class Content(WebsiteGenerator):

    def autoname(self):
        # content_type must exist for prefix
        prefix = TYPE_PREFIX.get(self.content_type, "g")

        # always generate slug from title (slug is read_only)
        if not self.slug:
            self.slug = slugify(self.title)

        self.slug = slugify(self.slug)
        ensure_unique_slug(self, prefix)

        # ✅ stable unique key
        # name becomes "docs/install-guide" etc.
        self.name = f"{prefix}/{self.slug}"

    def validate(self):
        # route must always match
        prefix = TYPE_PREFIX.get(self.content_type, "g")
        self.route = f"{prefix}/{self.slug}"
        self.content_key = self.route  # add field in doctype

        # SEO defaults
        if not self.meta_title:
            self.meta_title = (self.title or "")[:60]
        if not self.meta_description and self.summary:
            self.meta_description = (self.summary or "")[:160]

        # publish flags
        is_published = (self.status == "Published" and int(self.is_public or 0) == 1)
        self.published = 1 if is_published else 0

        if is_published and not self.published_on:
            self.published_on = now_datetime()

        # tags normalized (store normalized CSV)
        norm = normalize_tags_csv(self.tags or "")
        self.tags = ", ".join(norm)
        self.tags_normalized = ", ".join(norm)

        # search_text (hidden field) - keep it lightweight
        body_plain = strip_html(self.body_md or "")
        body_plain = re.sub(r"\s+", " ", body_plain).strip()

        self.search_text = " | ".join(
            filter(None, [
                self.title,
                self.summary,
                body_plain[:8000],  # cap to avoid huge DB writes
                self.tags,
                self.category,
                self.content_type,
            ])
        )

    def get_context(self, context):
        related = []
        if self.category:
            related = frappe.get_all(
                "Content",
                filters={
                    "published": 1,
                    "is_public": 1,
                    "content_type": self.content_type,
                    "category": self.category,
                    "name": ["!=", self.name],
                },
                fields=["title", "route", "summary", "content_type", "hero_image"],
                order_by="published_on desc, modified desc",
                limit_page_length=6,
            )

        context.related_items = related
        context.page_title = self.title
        return context

# import re
# import frappe
# from frappe.website.website_generator import WebsiteGenerator
# from frappe.utils import now_datetime

# _slug_rx = re.compile(r"[^a-z0-9-]+")

# TYPE_PREFIX = {
#     "Doc": "docs",
#     "Tutorial": "tutorials",
#     "Wiki": "wiki",
#     "Note": "notes",
#     "Profile": "profiles",
#     "Article": "articles",
#     "HowTo": "howto",
#     "FAQ": "faq",
#     "Portfolio": "portfolio",
#     "Jobs": "jobs",
#     "Projects": "projects",
#     "Post": "posts",
# }

# def slugify(txt: str) -> str:
#     s = (txt or "").strip().lower().replace(" ", "-")
#     s = _slug_rx.sub("-", s)
#     s = re.sub(r"-{2,}", "-", s).strip("-")
#     return s or "page"

# class Content(WebsiteGenerator):
#     # optional: if you created a custom template file
#     # template = "templates/content/content.html"

#     def autoname(self):
#         if not self.slug and self.title:
#             self.slug = slugify(self.title)
#         else:
#             self.slug = slugify(self.slug)

#         self.name = self.slug  # because autoname is field:slug

#     def validate(self):
#         super().validate()

#         prefix = TYPE_PREFIX.get(self.content_type, "g")
#         self.route = f"{prefix}/{self.slug}"

#         if not self.meta_title:
#             self.meta_title = (self.title or "")[:60]
#         if not self.meta_description and self.summary:
#             self.meta_description = (self.summary or "")[:160]

#         is_published = (self.status == "Published" and int(self.is_public or 0) == 1)
#         self.published = 1 if is_published else 0

#         if is_published and not self.published_on:
#             self.published_on = now_datetime()

#     def get_context(self, context):
#         # DO NOT call super().get_context(context) — it doesn't exist on WebsiteGenerator
#         related = []
#         if self.category:
#             related = frappe.get_all(
#                 "Content",
#                 filters={
#                     "published": 1,
#                     "is_public": 1,
#                     "content_type": self.content_type,
#                     "category": self.category,
#                     "name": ["!=", self.name],
#                 },
#                 fields=["title", "route", "summary"],
#                 order_by="published_on desc, modified desc",
#                 limit_page_length=6,
#             )

#         context.related_items = related
#         context.page_title = self.title
#         return context

# import re
# import frappe
# from frappe.website.website_generator import WebsiteGenerator
# from frappe.utils import now_datetime

# _slug_rx = re.compile(r"[^a-z0-9-]+")

# TYPE_PREFIX = {
#     "Doc": "docs",
#     "Tutorial": "tutorials",
#     "Wiki": "wiki",
#     "Note": "notes",
#     "Profile": "profiles",
#     "Article": "articles",
#     "HowTo": "howto",
#     "FAQ": "faq",
#     "Portfolio": "portfolio",
#     "Jobs": "jobs",
#     "Projects": "projects",
#     "Post": "posts",
# }

# def slugify(txt: str) -> str:
#     s = (txt or "").strip().lower().replace(" ", "-")
#     s = _slug_rx.sub("-", s)
#     s = re.sub(r"-{2,}", "-", s).strip("-")
#     return s or "page"

# class Content(WebsiteGenerator):
#     def autoname(self):
#         # slug must exist BEFORE autoname=field:slug can work
#         if not self.slug and self.title:
#             self.slug = slugify(self.title)
#         else:
#             self.slug = slugify(self.slug)

#         # name = slug (because DocType uses autoname: field:slug)
#         self.name = self.slug

#     def validate(self):
#         super().validate()

#         prefix = TYPE_PREFIX.get(self.content_type, "g")

#         # route auto (no manual typing)
#         self.route = f"{prefix}/{self.slug}"

#         # meta defaults
#         if not self.meta_title:
#             self.meta_title = (self.title or "")[:60]
#         if not self.meta_description and self.summary:
#             self.meta_description = (self.summary or "")[:160]

#         # publish bookkeeping
#         is_published = (self.status == "Published" and int(self.is_public or 0) == 1)
#         self.published = 1 if is_published else 0

#         if is_published and not self.published_on:
#             self.published_on = now_datetime()
    
    # def get_context(self, context):
    #     super().get_context(context)
    #     related = []
    #     if self.category:
    #         related = frappe.get_all(
    #             "Content",
    #             filters={
    #                 "published": 1,
    #                 "is_public": 1,
    #                 "content_type": self.content_type,
    #                 "category": self.category,
    #                 "name": ["!=", self.name],
    #             },
    #             fields=["title", "route", "summary"],
    #             order_by="published_on desc, modified desc",
    #             limit_page_length=6,
    #         )
    #     context.related_items = related
