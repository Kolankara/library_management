from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    """
        method generates shelf details
        Args:
            filters(Frappe dict): contains selected shelf for details
        Returns:
            columns: serial number and articles
            data: list of shelves with articles
    """
    # Get the shelf ID from filters
    shelf_id = filters.get("shelf")
    
    # Fetch the shelf document
    shelf = frappe.get_doc('Shelf', shelf_id)
    
    # Fetch all articles for the specified shelf
    articles_by_row = frappe.get_all(
        'Article',
        filters={'shelf_name': shelf_id},
        fields=['row_no', 'article_name'],
        order_by='row_no'
    )
    
    # Organize articles by row number
    articles_dict = {}
    for article in articles_by_row:
        row = article['row_no']
        if row not in articles_dict:
            articles_dict[row] = []
        articles_dict[row].append(article['article_name'])
    
    # Determine the number of columns needed
    max_articles_per_row = max(len(articles) for articles in articles_dict.values()) if articles_dict else 0
    
    # Define columns, omitting 'row_no'
    columns = [{'fieldname': f'article_{i+1}',
                'label': _(f'Article {i+1}'), 
                'fieldtype': 'Data', 'width': 250} 
                for i in range(max_articles_per_row)]
    
    # Prepare data
    data = []
    for row in range(1, shelf.no_of_rows + 1):
        row_data = {}
        articles = articles_dict.get(row, [])
        
        for col in range(max_articles_per_row):
            row_data[f'article_{col+1}'] = articles[col] if col < len(articles) else ''
        
        data.append(row_data)
    
    # Return columns and data
    return columns, data
