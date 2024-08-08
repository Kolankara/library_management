import frappe
from frappe.model.document import Document

class Article(Document):

    def before_insert(self):
        """
        Override before_insert to update shelf capacity and assign row_no and position.
        """
        if self.status != 'Issued':
            self.assign_row_and_position()
        else:
            frappe.msgprint("Cannot assign position for an issued article.")

    def assign_row_and_position(self):
        """
        Assign row_no and position for the article based on the available shelf.
        """
        shelves = frappe.get_all('Shelf', filters={'genre': self.genre},
                                 fields=['name', 'no_of_rows', 'row_capacity',
                                         'row_current_capacity', 'current_row'])
        
        if not shelves:
            frappe.throw(f"No shelf found for the genre '{self.genre}'")
        
        shelf_doc = frappe.get_doc('Shelf', shelves[0]['name'])
        available_row = self.find_available_row(shelf_doc)
        if not available_row:
            frappe.throw(f"No available rows in the shelf for genre '{self.genre}'")
        self.row_no = available_row['row_no']
        self.position = available_row['position']
        shelf_doc.row_current_capacity -= 1
        if shelf_doc.row_current_capacity == 0:
            if shelf_doc.current_row == shelf_doc.no_of_rows:
                frappe.msgprint(f"No more rows available in Shelf '{shelf_doc.name}'")
            else:
                self.update_shelf_position(shelf_doc)
        shelf_doc.save()

    def find_available_row(self, shelf_doc):
        """
        Find an available row and its position.
        """
        existing_articles = frappe.get_all('Article', filters={'genre': self.genre,
                                           'row_no': shelf_doc.current_row},
                                           fields=['row_no', 'position'])
        next_position = len(existing_articles) + 1
        if next_position > shelf_doc.row_capacity:
            self.update_shelf_position(shelf_doc)
            next_position = 1
        return {'row_no': shelf_doc.current_row, 'position': next_position}

    def update_shelf_position(self, shelf_doc):
        """
        Update the shelf's row_current_capacity and move to the next row when 
        the current row is full.
        """
        next_row_no = shelf_doc.current_row + 1
        if next_row_no > shelf_doc.no_of_rows:
            frappe.msgprint(f"No more rows available in Shelf '{shelf_doc.name}'")
            return
        shelf_doc.current_row = next_row_no
        shelf_doc.row_current_capacity = shelf_doc.row_capacity
        shelf_doc.save()
        
        frappe.msgprint(
        f"Updated current_row to {next_row_no} and reset row_current_capacity for Shelf '{shelf_doc.name}'")
   
    def before_save(self):
        """
        Override before_save to ensure shelf name is updated based on genre.
        """
        self.update_shelf_name()

    def update_shelf_name(self):
        """
        Fetch and set the shelf name based on the genre.
        """
        if self.genre:
            shelf = frappe.get_all('Shelf',filters={'genre': self.genre}, 
                                   fields=['name'], limit=1)
            if shelf:
                self.shelf_name = shelf[0].name
            else:
                self.shelf_name = None
                frappe.msgprint(f"No shelf found for the genre '{self.genre}'")
        else:
            self.shelf_name = None
            frappe.msgprint("Genre is not selected")
