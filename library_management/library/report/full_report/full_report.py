from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
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
            'label': _('membership_from'),
            'fieldtype': 'Date',
           
		},
        {
            'fieldname': 'to_date',
            'label': _('membership_to'),
            'fieldtype': 'Date',
           
		},
        {
            'fieldname': 'membership_status',
            'label': _('Membership Status'),
            'fieldtype': 'Data',
            'width': 150
        },
        # {
        #     'fieldname': 'current_article',
        #     'label': _('Current Article Held'),
        #     'fieldtype': 'Data',
        #     'width': 150
        # },
	]

    members = frappe.db.get_list("Library Member", fields=["fullname", "email_address", "phone", "name"])
    today = frappe.utils.nowdate()
    data = []
    for i in members:
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": i["name"],
                "docstatus": 1,
                "from_date": ("<", today),
                "to_date": (">", today),
            }
        )
       
         
		 
            
        membership_status = "Valid Membership" if valid_membership else "No Membership"

        # latest_issue_transaction = frappe.db.get_list(
        #     'Library Transaction',
        #     filters={"type": "Issue", "docstatus": 1, "library_member": i["name"]},
        #     fields=["name", "article", "date"],
        #     order_by="date desc",
        #     limit=1
        # )

        # current_article = "No Articles Issued"

        # if latest_issue_transaction and latest_issue_transaction[0].get("article"):
        #     issued_article = latest_issue_transaction[0]["article"]
        #     latest_issue_date = latest_issue_transaction[0]["date"]

        #     # Check if there is a return transaction for this article after the issue date
        #     return_transaction = frappe.db.get_list(
        #         'Library Transaction',
        #         filters={
        #             "type": "Return",
        #             "docstatus": 1,
        #             "library_member": i["name"],
        #             "article": issued_article,
        #             "date": (">", latest_issue_date)
        #         },
        #         fields=["name"]
        #     )

        #     if not return_transaction:
        #         current_article = issued_article

        membership=frappe.db.exists('Library membership',{"library_member":i.name,"docstatus":1})
        from_date,to_date = None,None
        if membership:
            memberhsip_from = frappe.db.get_last_doc("Library Membership",{"library_member":i.name},order_by="from_date asc")
            from_date,to_date=memberhsip_from.from_date,memberhsip_from.to_date
            print(from_date)
        data.append({
            'fullname': i["fullname"],
            'email_address': i["email_address"],
            'phone': i["phone"],
            'from_date':from_date,
            'to_date':to_date,
            'membership_status': membership_status
        })

    return columns, data
