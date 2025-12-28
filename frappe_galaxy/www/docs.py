import frappe

def get_context(context):
    context.no_cache = 1

    category_slug = frappe.form_dict.get("category")
    context.category_slug = category_slug
    context.page_title = "Docs"

    category_name = None
    category_title = None

    if category_slug:
        category_name, category_title = frappe.db.get_value(
            "Category",
            {"slug": category_slug},
            ["name", "title"]
        ) or (None, None)

    filters = {"published": 1, "is_public": 1, "content_type": "Doc"}
    if category_name:
        filters["category"] = category_name

    context.items = frappe.get_all(
        "Content",
        filters=filters,
        fields=["title", "route", "summary", "published_on"],
        order_by="published_on desc, modified desc",
        limit_page_length=50
    )

    context.active_category_title = category_title

    context.categories = frappe.get_all(
        "Category",
        fields=["title", "slug", "lft"],
        order_by="lft asc",
        limit_page_length=500
    )
