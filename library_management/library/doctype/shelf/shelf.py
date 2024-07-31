# Copyright (c) 2024, Nandana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Shelf(Document):
    def before_save(self):
        """Override before_save to ensure row_current_capacity and current_row are set."""
        if self.row_current_capacity is None:
            self.row_current_capacity = self.row_capacity
        if self.current_row is None:
            self.current_row = 1  # Initialize to the first row

def initialize_shelves():
    """Initialize row_current_capacity and current_row for all existing shelves."""
    shelves = frappe.get_all('Shelf', fields=['name'])
    for shelf in shelves:
        initialize_shelf_capacity(shelf['name'])

def initialize_shelf_capacity(shelf_id):
    """Initialize the row_current_capacity and current_row of a shelf."""
    shelf_doc = frappe.get_doc('Shelf', shelf_id)
    if shelf_doc.row_current_capacity is None:
        shelf_doc.row_current_capacity = shelf_doc.row_capacity
    if shelf_doc.current_row is None:
        shelf_doc.current_row = 1  # Initialize to the first row
    shelf_doc.save()
    frappe.msgprint(f"Initialized row_current_capacity and current_row for Shelf ID {shelf_id}")

def on_doctype_update():
    """Ensure shelves are initialized on system setup."""
    initialize_shelves()
