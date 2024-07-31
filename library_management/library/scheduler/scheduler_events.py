import frappe
from datetime import datetime, timedelta

def send_overdue_notifications():
    transactions = frappe.get_list("Library Transaction",
        filters={"docstatus": 1},
        fields=["name", "library_member", "date"])
    borrow_period = frappe.db.get_single_value("Library Settings", "book_borrow_period") 

    for i in transactions:
        added_articles = frappe.get_list("Add Article",
            filters={"parent": i.name, "type": "Issue"},
            fields=["article_name"])

        for article in added_articles:
            return_date = i.date + timedelta(days=borrow_period)  
            notification_date = return_date - timedelta(days=2)

            current_date = datetime.now().date()

            if current_date == notification_date:
                create_notification_log(article.article_name, i.library_member)
    print("hello")

def create_notification_log(doc, recipient, subject, content, type = None):
    ''' method is used to create notification log
        args:
            doc: document object
            recipient: notification receiving user
            subject: subject of notification log
            type: type of the notification log '''
    notification_log = frappe.new_doc('Notification Log')
    notification_log.type = 'Alert'
    if type:
        notification_log.type = type
    notification_log.document_type = doc.doctype
    notification_log.document_name = doc.name
    notification_log.for_user = recipient
    notification_log.subject = subject
    notification_log.email_content = content
    notification_log.save(ignore_permissions = True)