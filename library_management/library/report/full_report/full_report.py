from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    """
    Generates a report with library member details including membership status, period, and current articles.
    
    Args:
        filters (dict, optional): Dictionary containing filter values for the report.
    
    Returns:
        columns (list): List of dictionaries defining the columns of the report.
        data (list): List of dictionaries containing the member data for the report.
    """
    columns = [
        {
            'fieldname': 'fullname',
            'label': _('Full Name'),
            'fieldtype': 'Data',
            'width': 250
        },
        {
            'fieldname': 'email_address',
            'label': _('Email Address'),
            'fieldtype': 'Data',
            'width': 250
        },
        {
            'fieldname': 'phone',
            'label': _('Phone'),
            'fieldtype': 'Data',
            'width': 150
        },
        {
            'fieldname': 'from_date',
            'label': _('Membership From'),
            'fieldtype': 'Date',
        },
        {
            'fieldname': 'to_date',
            'label': _('Membership To'),
            'fieldtype': 'Date',
        },
        {
            'fieldname': 'membership_status',
            'label': _('Membership Status'),
            'fieldtype': 'Data',
            'width': 150
        },
        {
            'fieldname': 'current_articles',
            'label': _('Current Articles Held'),
            'fieldtype': 'Data',
            'width': 250
        },
    ]

    today = frappe.utils.nowdate()
    
    
    members = frappe.db.get_list("Library Member",
                                 fields=["fullname", "email_address",
                                         "phone", "name"])
    data = []
    for member in members:
        memberships = frappe.db.get_list(
            "Library Membership",
            filters={
                "library_member": member["name"],
                "docstatus": 1,
                "from_date": ("<", today),
                "to_date": (">", today),
            },
            fields=["from_date", "to_date"],
            order_by="from_date desc",
            limit=1
        )
        if memberships:
            membership = memberships[0]
            membership_status = "Valid Membership"
            from_date = membership["from_date"]
            to_date = membership["to_date"]
        else:
            membership_status = "No Membership"
            from_date = to_date = None
        
        issue_transactions = frappe.db.get_list(
            'Library Transaction',
            filters={"type": "Issue", "docstatus": 1,
                     "library_member": member["name"]},
            fields=["name"],
            order_by="date desc"
        )
        
        current_articles = []
        
        for issue in issue_transactions:
            issue_name = issue["name"]
            
            
            issue_articles = frappe.get_doc(
                'Library Transaction', issue_name).articles
            
            for article in issue_articles:
               
                return_transactions = frappe.db.get_list(
                    'Library Transaction',
                    filters={
                        "type": "Return",
                        "docstatus": 1,
                        "library_member": member["name"],
                        "article": article.article,
                        "date": (">", issue.date)
                    },
                    fields=["name"]
                )
                
                if not return_transactions:
                    if article.article not in current_articles:
                        current_articles.append(article.article)
        
   
        current_articles_str = ', '.join(current_articles) if current_articles else "No Articles Issued"
        
        data.append({
            'fullname': member["fullname"],
            'email_address': member["email_address"],
            'phone': member["phone"],
            'from_date': from_date,
            'to_date': to_date,
            'membership_status': membership_status,
            'current_articles': current_articles_str
        })

    return columns, data