import frappe

TYPE_META = {
    "Doc": {"title": "Docs", "base": "docs"},
    "Tutorial": {"title": "Tutorials", "base": "tutorials"},
    "Wiki": {"title": "Wiki", "base": "wiki"},
    "Note": {"title": "Notes", "base": "notes"},
    "Profile": {"title": "Profiles", "base": "profiles"},
    "Article": {"title": "Articles", "base": "articles"},
    "HowTo": {"title": "HowTo", "base": "howto"},
    "FAQ": {"title": "FAQ", "base": "faq"},
    "Portfolio": {"title": "Portfolio", "base": "portfolio"},
    "Jobs": {"title": "Jobs", "base": "jobs"},
    "Projects": {"title": "Projects", "base": "projects"},
    "Post": {"title": "Posts", "base": "posts"},
}

def get_context(context):
    context.no_cache = 1

    # route defaults come here
    content_type = (frappe.form_dict.get("content_type") or "").strip()
    if content_type not in TYPE_META:
        # safe fallback
        content_type = "Doc"

    category_slug = frappe.form_dict.get("category")

    context.content_type = content_type
    context.type_title = TYPE_META[content_type]["title"]
    context.base_path = TYPE_META[content_type]["base"]
    context.category_slug = category_slug

    # resolve category from slug
    category_name = None
    category_title = None
    if category_slug:
        row = frappe.db.get_value("Galaxy Category", {"slug": category_slug}, ["name", "title"], as_dict=True)
        if row:
            category_name = row.name
            category_title = row.title

    context.active_category_title = category_title

    # filters
    filters = {
        "published": 1,
        "is_public": 1,
        "content_type": content_type,
    }
    if category_name:
        filters["category"] = category_name

    # list items
    context.items = frappe.get_all(
        "Content",
        filters=filters,
        fields=["title", "route", "summary", "published_on", "tags", "category"],
        order_by="published_on desc, modified desc",
        limit_page_length=50,
    )

    # sidebar categories (tree order)
    context.categories = frappe.get_all(
        "Galaxy Category",
        fields=["title", "slug", "lft"],
        order_by="lft asc",
        limit_page_length=500,
    )
