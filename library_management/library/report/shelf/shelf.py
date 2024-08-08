from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    """
    Method generates shelf details.
    Args:
        filters (Frappe dict): Contains selected shelf for details.
    Returns:
        columns: Serial number and articles.
        data: List of shelves with articles.
    """
    
    shelf_id = filters.get("shelf")
    no_of_rows = frappe.get_value('Shelf', shelf_id, 'no_of_rows')
    # Gets all data from Article doctype
    articles_by_row = frappe.get_all(
        'Article',
        filters={'shelf_name': shelf_id},
        fields=['row_no', 'article_name'],
        order_by='row_no'
    )
    
    articles_dict = {}
    for article in articles_by_row:
        row = article['row_no']
        if row not in articles_dict:
            articles_dict[row] = []
        articles_dict[row].append(article['article_name'])
    
    max_articles_per_row = max(len(articles) for articles in articles_dict.values()) if articles_dict else 0
    
    columns = [{'fieldname': f'article_{i+1}',
                'label': _(f'Article {i+1}'), 
                'fieldtype': 'Data', 'width': 250} 
                for i in range(max_articles_per_row)]
    
    data = []
    for row in range(1, no_of_rows + 1):
        row_data = {}
        articles = articles_dict.get(row, [])
        
        for col in range(max_articles_per_row):
            row_data[f'article_{col+1}'] = articles[col] if col < len(articles) else ''
        
        data.append(row_data)
    
    return columns, data
