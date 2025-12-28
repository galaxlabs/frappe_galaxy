import frappe

def update_website_context(context):
    # Root navbar items from Category
    context.nav_items = frappe.get_all(
        "Category",
        filters={
            "is_active": 1,
            "show_in_nav": 1,
            "is_group": 1,
            "parent_category": ["in", ["", None]],
        },
        fields=["title", "slug", "icon", "sort_order"],
        order_by="sort_order asc, title asc",
        limit_page_length=50,
    )
    return context
