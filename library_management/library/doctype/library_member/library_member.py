# Copyright (c) 2024, Nandana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LibraryMember(Document):
    #this method will run every time a document is saved
    def before_save(self):
        self.fullname = f'{self.firstname} {self.lastname or ""}'

# library_management/library_management/doctype/library_member/library_member.py





