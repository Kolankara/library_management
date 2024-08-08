# Copyright (c) 2024, Nandana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class Reservation(Document):
    def before_submit(self):
        """
        Method to handle actions before submitting the reservation.
        Sets the status of the article to "Reserved".
        """
        article = frappe.get_doc("Article", self.article_name)
        article.status = "Reserved"
        article.save()
            
@frappe.whitelist()
def custom_query(doctype,txt,searchfield,start,page_len,filter):
    """
    Custom query to fetch valid library members based on their membership status.
    
    Args:
        doctype (str): The name of the doctype to search.
        txt (str): The search text.
        searchfield (str): The field to search.
        start (int): The start index of the search results.
        page_len (int): The number of search results to return.
        filters (dict): Additional filters for the search.
    
    Returns:
        list: List of valid library members.
    """
    today= datetime.now().date()
    valid_memberships = frappe.get_all(
        "Library Membership",
        filters={
            "docstatus": 1,
            "from_date": ("<=", today),
            "to_date": (">=", today),
        },
            pluck="library_member",
    )
    return [[member] for member in valid_memberships] or []
