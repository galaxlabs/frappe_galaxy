import json
import frappe
from frappe.utils import now

ALLOWED_REVIEW_ROLES = {"Moderator", "Editor", "System Manager"}

def _has_any_role(roles):
    user_roles = set(frappe.get_roles(frappe.session.user))
    return bool(user_roles.intersection(set(roles)))

def _extract_docname_from_request():
    """DocType Action may send doc as JSON string/dict. Also sometimes sends docname/name."""
    fd = frappe.form_dict or {}

    # direct fields
    name = fd.get("name") or fd.get("docname") or fd.get("contribution_name")
    if name:
        return name

    # doc payload (string/dict)
    doc = fd.get("doc")
    if doc:
        if isinstance(doc, str):
            try:
                doc = json.loads(doc)
            except Exception:
                doc = None
        if isinstance(doc, dict):
            return doc.get("name")

    # docs payload (sometimes list)
    docs = fd.get("docs")
    if docs:
        if isinstance(docs, str):
            try:
                docs = json.loads(docs)
            except Exception:
                docs = None
        if isinstance(docs, list) and docs:
            return (docs[0] or {}).get("name")

    return None

@frappe.whitelist()
def review_contribution(contribution_name=None, action=None):
    if not contribution_name:
        contribution_name = _extract_docname_from_request()

    if not action:
        action = (frappe.form_dict or {}).get("action")

    if not contribution_name or not action:
        frappe.throw("Missing contribution_name/name or action")

    action = (action or "").lower().strip()
    if action not in ("approve", "reject"):
        frappe.throw("Invalid action. Use approve/reject")

    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    if not _has_any_role(ALLOWED_REVIEW_ROLES):
        frappe.throw("Not permitted", frappe.PermissionError)

    doc = frappe.get_doc("Galaxy Contribution", contribution_name)

    if action == "reject":
        doc.db_set("status", "Rejected", update_modified=False)
        doc.db_set("reviewed_by", frappe.session.user, update_modified=False)
        doc.db_set("reviewed_on", now(), update_modified=False)
        return {"ok": True, "status": "Rejected"}

    # approve
    content = frappe.get_doc("Galaxy Content", doc.content)

    if doc.contribution_type in ("Suggest Edit", "FixTypo", "Add Example") and doc.proposed_md:
        content.db_set("body_md", doc.proposed_md, update_modified=False)

    doc.db_set("status", "Approved", update_modified=False)
    doc.db_set("reviewed_by", frappe.session.user, update_modified=False)
    doc.db_set("reviewed_on", now(), update_modified=False)

    return {"ok": True, "status": "Approved", "content": content.name}

@frappe.whitelist()
def reject_contribution(name=None, **kwargs):
    contribution_name = name or _extract_docname_from_request()
    return review_contribution(contribution_name=contribution_name, action="reject")

@frappe.whitelist()
def approve_contribution(name=None, **kwargs):
    contribution_name = name or _extract_docname_from_request()
    return review_contribution(contribution_name=contribution_name, action="approve")



@frappe.whitelist()
def mark_solution(reply_name=None, reply=None, name=None, doc=None):
    """
    Works for:
    - manual API calls: args {reply_name: "..."} or {reply: "..."} or {name: "..."}
    - DocType Server Action: often sends `doc` (JSON/string) or sometimes sends nothing
    """

    # 1) Try direct args first
    reply_name = reply_name or reply or name

    # 2) If not provided, try to extract from `doc`
    if not reply_name and doc:
        # doc may come as dict or JSON string
        if isinstance(doc, str):
            try:
                doc = json.loads(doc)
            except Exception:
                doc = None

        if isinstance(doc, dict):
            reply_name = doc.get("name")

    # 3) Last fallback: try frappe.form_dict
    if not reply_name:
        reply_name = frappe.form_dict.get("reply_name") or frappe.form_dict.get("name")

    if not reply_name:
        frappe.throw("reply_name is required")

    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    if not _has_any_role(ALLOWED_REVIEW_ROLES):
        frappe.throw("Not permitted", frappe.PermissionError)

    reply_doc = frappe.get_doc("Galaxy Reply", reply_name)
    thread_doc = frappe.get_doc("Galaxy Thread", reply_doc.thread)

    # Unset previous solution
    if thread_doc.solution_reply and thread_doc.solution_reply != reply_doc.name:
        old = frappe.get_doc("Galaxy Reply", thread_doc.solution_reply)
        old.db_set("is_solution", 0, update_modified=False)
        old.db_set("solution_on", None, update_modified=False)
        old.db_set("solution_by", None, update_modified=False)

    # Set solution
    reply_doc.db_set("is_solution", 1, update_modified=False)
    reply_doc.db_set("solution_on", now(), update_modified=False)
    reply_doc.db_set("solution_by", frappe.session.user, update_modified=False)

    thread_doc.db_set("solution_reply", reply_doc.name, update_modified=False)
    thread_doc.db_set("status", "Answered", update_modified=False)

    return {"ok": True, "thread": thread_doc.name, "solution_reply": reply_doc.name}


@frappe.whitelist(allow_guest=True)
def list_content(content_type="Doc", limit=20, start=0, category=None, search=None):
    filters = {"published": 1, "is_public": 1, "content_type": content_type}

    if category:
        filters["category"] = category

    fields = ["name", "title", "slug", "summary", "content_type", "published_on", "category", "tags", "hero_image"]

    q = frappe.qb.from_("tabGalaxy Content").select(*[frappe.qb.Field(f) for f in fields])

    for k, v in filters.items():
        q = q.where(frappe.qb.Field(k) == v)

    if search:
        like = f"%{search}%"
        q = q.where(
            (frappe.qb.Field("title").like(like)) |
            (frappe.qb.Field("summary").like(like)) |
            (frappe.qb.Field("tags").like(like))
        )

    q = q.orderby(frappe.qb.Field("published_on"), order=frappe.qb.desc).limit(int(limit)).offset(int(start))

    return {"items": q.run(as_dict=True)}

@frappe.whitelist(allow_guest=True)
def get_content_by_slug(slug):
    doc = frappe.get_all(
        "Galaxy Content",
        filters={"slug": slug, "published": 1, "is_public": 1},
        fields=["name", "title", "slug", "summary", "body_md", "content_type", "published_on", "category", "tags", "hero_image", "canonical_url", "meta_title", "meta_description"],
        limit=1
    )
    if not doc:
        frappe.throw("Not found")
    return doc[0]

@frappe.whitelist()
def create_contribution(content, contribution_type="Comment", comment_text=None, proposed_md=None):
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    d = frappe.get_doc({
        "doctype": "Galaxy Contribution",
        "content": content,
        "contribution_type": contribution_type,
        "comment_text": comment_text,
        "proposed_md": proposed_md,
        "status": "Pending",
        "contributor": frappe.session.user,
    })
    d.insert(ignore_permissions=True)
    return {"ok": True, "name": d.name, "status": d.status, "created_on": now()}
