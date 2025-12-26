import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def mark_solution(reply: str):
    """Mark a Galaxy Reply as the accepted solution for its thread."""
    reply_doc = frappe.get_doc("Galaxy Reply", reply)
    thread_doc = frappe.get_doc("Galaxy Thread", reply_doc.thread)

    # Permission rule (MVP):
    # - Thread owner OR Moderator/System Manager can mark solution
    allowed = (
        frappe.session.user == thread_doc.created_by
        or frappe.has_role("System Manager")
        or frappe.has_role("Galaxy Moderator")
    )
    if not allowed:
        frappe.throw("Not permitted")

    # Unset previous solution(s)
    frappe.db.sql("""
        UPDATE `tabGalaxy Reply`
        SET is_solution = 0, solution_on = NULL, solution_by = NULL
        WHERE thread = %s
    """, (thread_doc.name,))

    # Set this reply as solution
    reply_doc.db_set("is_solution", 1)
    reply_doc.db_set("solution_on", now_datetime())
    reply_doc.db_set("solution_by", frappe.session.user)

    # Update thread
    thread_doc.db_set("solution_reply", reply_doc.name)
    thread_doc.db_set("status", "Answered")

    return {"ok": True, "thread": thread_doc.name, "reply": reply_doc.name}


@frappe.whitelist()
def mark_solution(content_name: str):
    if frappe.session.user == "Guest":
        frappe.throw("Login required")

    existing = frappe.get_all(
        "Galaxy Solution Vote",
        filters={"content": content_name, "user": frappe.session.user},
        pluck="name",
        limit=1
    )

    if existing:
        doc = frappe.get_doc("Galaxy Solution Vote", existing[0])
    else:
        doc = frappe.new_doc("Galaxy Solution Vote")
        doc.content = content_name
        doc.user = frappe.session.user

    doc.is_solution = 1
    doc.save(ignore_permissions=True)
    return {"ok": True}