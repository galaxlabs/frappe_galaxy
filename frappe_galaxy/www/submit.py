import frappe

def get_context(context):
    context.no_cache = 1
    context.title = "Submit Content"

    # must be logged in
    if frappe.session.user == "Guest":
        frappe.throw("Please login to submit content", frappe.PermissionError)

    context.content_types = [
        "Doc","Tutorial","Wiki","Note","Profile","Article","HowTo","FAQ",
        "Portfolio","Jobs","Projects","Post"
    ]

    # categories list
    context.categories = frappe.get_all(
        "Galaxy Category",
        fields=["name", "title"],
        order_by="lft asc",
        limit_page_length=500
    )
