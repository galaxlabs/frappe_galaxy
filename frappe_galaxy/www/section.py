import frappe


def get_context(context):
    context.no_cache = 1

    # root section comes from route: /docs => "docs"
    # frappe.path is available in website context in most cases,
    # but safest: use request.path
    path = (frappe.local.request.path or "/").strip("/")
    root_slug = path.split("/")[0] if path else "docs"

    # allow explicit override (?section=docs) if needed
    root_slug = (frappe.form_dict.get("section") or root_slug).strip() or "docs"

    # selected category from query param
    active_slug = (frappe.form_dict.get("category") or "").strip()

    # resolve root category
    root = frappe.db.get_value("Category", {"slug": root_slug}, ["name", "title", "lft", "rgt"], as_dict=True)
    if not root:
        frappe.throw("Section not found")

    context.section_slug = root_slug
    context.section_title = root.title

    # resolve active category (must be inside root tree)
    active = None
    if active_slug:
        row = frappe.db.get_value("Category", {"slug": active_slug}, ["name", "title", "lft", "rgt"], as_dict=True)
        if row and row.lft >= root.lft and row.rgt <= root.rgt:
            active = row

    context.active_category_title = active.title if active else None
    context.active_category_slug = active_slug if active else None

    # sidebar categories: only inside this section tree
    context.categories = frappe.get_all(
        "Category",
        filters={
            "is_active": 1,
            "lft": [">=", root.lft],
            "rgt": ["<=", root.rgt],
        },
        fields=["name", "title", "slug", "parent_category", "is_group", "lft"],
        order_by="lft asc",
        limit_page_length=500,
    )

    # content filters: choose active category tree if selected, else root tree
    tree = active or root

    # get categories under selected tree
    category_names = frappe.get_all(
        "Category",
        filters={"lft": [">=", tree.lft], "rgt": ["<=", tree.rgt], "is_active": 1},
        pluck="name",
        limit_page_length=1000,
    )

    content_filters = {
        "published": 1,
        "is_public": 1,
        "category": ["in", category_names] if category_names else "",
    }

    context.items = frappe.get_all(
        "Content",
        filters=content_filters,
        fields=["title", "route", "summary", "published_on", "tags", "category"],
        order_by="published_on desc, modified desc",
        limit_page_length=50,
    )
