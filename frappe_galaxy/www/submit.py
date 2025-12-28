import frappe

def get_context(context):
    context.no_cache = 1
    context.title = "Submit Content"

    # Allow public OR keep login required (your choice)
    # If you want login required, uncomment below:
    # if frappe.session.user == "Guest":
    #     frappe.throw("Please login to submit content", frappe.PermissionError)

    context.content_types = [
        "Doc","Tutorial","Wiki","Note","Profile","Article","HowTo","FAQ",
        "Portfolio","Jobs","Projects","Post"
    ]

    # categories list (FIXED doctype name)
    context.categories = frappe.get_all(
        "Category",
        fields=["name", "title", "slug", "lft"],
        filters={"is_active": 1},
        order_by="lft asc",
        limit_page_length=500
    )
