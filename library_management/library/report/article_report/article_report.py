from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {
            'fieldname': 'article_name',
            'label': _('Article name'),
            'fieldtype': 'Link',
            'options':'Article',
        },
        {
            'fieldname': 'status',
            'label': _('Status'),
            'fieldtype': 'Select',
            'options': "\nIssued\nReturn"
        },
        {
            'fieldname': 'isbn',
            'label': _('ISBN'),
            'fieldtype': 'Data',
            'width': 450
        },
        {
            'fieldname': 'publisher',
            'label': _('Publisher'),
            'fieldtype': 'Data',
            'width': 450
        },
        {
            'fieldname': 'issue_count',
            'label': _('Issue Count'),
            'fieldtype': 'Int'
        },
         {
            'fieldname': 'return_count',
            'label': _('Return Count'),
            'fieldtype': 'Int'
        }
    ]

    
    articles = frappe.db.get_list("Article", fields=["name", "article_name", "status", "isbn", "publisher"])
    
    
    sub_trans = frappe.db.get_list('Library Transaction', filters={"type": "Issue", "docstatus": 1}, pluck="name")
    sub_trans_re = frappe.db.get_list("Library Transaction",filters={"type":"Return","docstatus":1},pluck="name")
    data = []
    for i in articles:
        
        issue_count = frappe.db.count("Add article", filters={"article": i["name"], "parent": ["in", sub_trans]})
        return_count=frappe.db.count("Add article",filters={"article": i["name"], "parent":["in",sub_trans_re]})
       
        data.append({
            'article_name': i["article_name"],
            'status': i["status"],
            'isbn': i["isbn"],
            'publisher': i["publisher"],
            'issue_count': issue_count,
            'return_count':return_count,
        })

    return columns, data
