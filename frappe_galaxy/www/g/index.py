import frappe

def get_context(context):
    context.no_cache = 1
    context.title = "Galaxy Guides"

    context.items = frappe.get_all(
        "Content",
        filters={"published": 1, "is_public": 1},
        fields=["title", "route", "content_type", "summary", "published_on", "category"],
        order_by="published_on desc, modified desc",
        limit_page_length=50
    )
