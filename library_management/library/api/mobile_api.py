import frappe

@frappe.whitelist()
def get_article(article_name):
    if frappe.db.exists("Article", article_name):
        return True
    else:
        return False