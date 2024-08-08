# Copyright (c) 2024, Nandana and contributors
# For license information, please see license.txt



import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus


class LibraryMembership(Document):
    def validate(self):
        """
        Method to validate the membership dates.
        Ensures that 'from_date' is earlier than 'to_date'.
        """
        if self.from_date and self.to_date and self.from_date > self.to_date:
            frappe.throw("from date must be earlier than to date")
            self.from_date = None
            self.to_date = None
    def before_submit(self):
        """
        Method to handle actions before submitting the membership.
        Ensures there is no overlapping active membership for the same member.
        Sets the 'to_date' based on the 'loan_period' from Library Settings.
        """
        exists = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": DocStatus.submitted(),
                "to_date": (">", self.from_date),
            },
        )
        if exists:
            frappe.throw("There is an active membership for this member")

        loan_period = frappe.db.get_single_value("Library Settings", "loan_period")
        self.to_date = frappe.utils.add_days(self.from_date, loan_period or 30)
