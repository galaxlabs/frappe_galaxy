import frappe

def get_context(context):
    context.no_cache = 1
    context.title = "Galaxy Guides"
    context.items = frappe.get_all(
        "Galaxy Content",
        filters={"status": "Published", "is_public": 1},
        fields=["title", "slug", "content_type", "summary", "published_on"],
        order_by="published_on desc, modified desc",
        limit=50
    )
