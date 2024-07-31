import frappe
def after_migrate():
    print("Migrated Successfully")

def after_insert(doc, method):
    if doc.doctype == "User":
        frappe.msgprint(f"New user created: {doc.first_name}, {doc.last_name}, {doc.email}")

# library_management/library_management/doctype/library_member/library_member.py


# 
def before_insert(doc, method):
    if doc.doctype == "Library Member":
        if doc.lastname == "s":
            doc.lastname = "doe"

