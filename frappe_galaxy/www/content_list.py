import frappe

TYPE_META = {
    "Doc": {"title": "Docs", "base": "docs"},
    "Tutorial": {"title": "Tutorials", "base": "tutorials"},
    "Wiki": {"title": "Wiki", "base": "wiki"},
    "Note": {"title": "Notes", "base": "notes"},
    "Profile": {"title": "Profiles", "base": "profiles"},
    "Article": {"title": "Articles", "base": "articles"},
    "HowTo": {"title": "How-To", "base": "howto"},
    "FAQ": {"title": "FAQ", "base": "faq"},
    "Portfolio": {"title": "Portfolio", "base": "portfolio"},
    "Jobs": {"title": "Jobs", "base": "jobs"},
    "Projects": {"title": "Projects", "base": "projects"},
    "Post": {"title": "Posts", "base": "posts"},
}

def _get_root_category(base_slug: str):
    return frappe.db.get_value(
        "Category",
        {"slug": base_slug},
        ["name", "title", "lft", "rgt"],
        as_dict=True
    )

def _get_sidebar_categories(root):
    if not root:
        return []

    # subtree (exclude root itself)
    return frappe.get_all(
        "Category",
        filters={
            "lft": [">", root.lft],
            "rgt": ["<", root.rgt],
            "is_active": 1,
        },
        fields=["title", "slug", "lft", "is_group", "parent_category"],
        order_by="lft asc",
        limit_page_length=500,
    )

def get_context(context):
    context.no_cache = 1

    # from route defaults
    content_type = (frappe.form_dict.get("content_type") or "").strip()
    if content_type not in TYPE_META:
        content_type = "Doc"

    meta = TYPE_META[content_type]
    base = meta["base"]

    context.content_type = content_type
    context.type_title = meta["title"]
    context.base_path = base

    # category comes from dynamic route: /docs/<category>
    category_slug = (frappe.form_dict.get("category") or "").strip()
    context.category_slug = category_slug

    # root section category: slug = docs/tutorials/wiki...
    root = _get_root_category(base)
    context.root_category_title = root.title if root else meta["title"]

    # sidebar only from this section
    context.categories = _get_sidebar_categories(root)

    # resolve selected category
    category_name = None
    category_title = None
    if category_slug:
        row = frappe.db.get_value(
            "Category",
            {"slug": category_slug},
            ["name", "title"],
            as_dict=True
        )
        if row:
            category_name = row.name
            category_title = row.title

    context.active_category_title = category_title

    # content filters
    filters = {
        "published": 1,
        "is_public": 1,
        "content_type": content_type,
    }
    if category_name:
        filters["category"] = category_name

    context.items = frappe.get_all(
        "Content",
        filters=filters,
        fields=["title", "route", "summary", "published_on", "tags"],
        order_by="published_on desc, modified desc",
        limit_page_length=50,
    )

# import frappe

# TYPE_META = {
#     "Doc": {"title": "Docs", "base": "docs"},
#     "Tutorial": {"title": "Tutorials", "base": "tutorials"},
#     "Wiki": {"title": "Wiki", "base": "wiki"},
#     "Note": {"title": "Notes", "base": "notes"},
#     "Profile": {"title": "Profiles", "base": "profiles"},
#     "Article": {"title": "Articles", "base": "articles"},
#     "HowTo": {"title": "How-To", "base": "howto"},
#     "FAQ": {"title": "FAQ", "base": "faq"},
#     "Portfolio": {"title": "Portfolio", "base": "portfolio"},
#     "Jobs": {"title": "Jobs", "base": "jobs"},
#     "Projects": {"title": "Projects", "base": "projects"},
#     "Post": {"title": "Posts", "base": "posts"},
# }

# def get_context(context):
#     context.no_cache = 1

#     content_type = (frappe.form_dict.get("content_type") or "").strip()
#     if content_type not in TYPE_META:
#         content_type = "Doc"

#     base = TYPE_META[content_type]["base"]
#     context.base_path = base
#     context.type_title = TYPE_META[content_type]["title"]

#     category_slug = frappe.form_dict.get("category")
#     context.category_slug = category_slug

#     # resolve root category by base slug (docs/tutorials/etc)
#     root = frappe.db.get_value("Category", {"slug": base}, ["name", "lft", "rgt", "title"], as_dict=True)

#     # sidebar categories in this section only
#     context.categories = []
#     if root:
#         context.categories = frappe.get_all(
#             "Category",
#             filters={
#                 "lft": [">", root.lft],
#                 "rgt": ["<", root.rgt],
#                 "is_active": 1,
#             },
#             fields=["title", "slug", "lft"],
#             order_by="lft asc",
#             limit_page_length=500,
#         )

#     # category filter
#     category_name = None
#     category_title = None
#     if category_slug:
#         row = frappe.db.get_value("Category", {"slug": category_slug}, ["name", "title"], as_dict=True)
#         if row:
#             category_name = row.name
#             category_title = row.title
#     context.active_category_title = category_title

#     filters = {"published": 1, "is_public": 1, "content_type": content_type}
#     if category_name:
#         filters["category"] = category_name

#     context.items = frappe.get_all(
#         "Content",
#         filters=filters,
#         fields=["title", "route", "summary", "published_on", "tags"],
#         order_by="published_on desc, modified desc",
#         limit_page_length=50,
#     )
