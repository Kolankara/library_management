import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus
from frappe.utils import flt, getdate, date_diff, nowdate

class LibraryTransaction(Document):
    def before_submit(self):
        """
        Method to handle actions before submitting the document.
        """
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()
            for article_entry in self.articles:
                article = frappe.get_doc("Article", article_entry.article)
                article.status = "Issued"
                article.save()  

        elif self.type == "Return":
            self.validate_return()
            self.before_save()
            for article_entry in self.articles:
                article = frappe.get_doc("Article", article_entry.article)
                article.status = "Available"
                article.save()

    def validate(self):
        """
        Method to validate the transaction.
        """
        self.validate_amount()

    def validate_issue(self):
        """
        Method to validate an 'Issue' transaction.
        """
        self.validate_membership()
        for article_entry in self.articles:
            article = frappe.get_doc("Article", article_entry.article)
            if article.status == "Issued":
                frappe.throw(
                    f"Article {article.name} is already issued by another member")

    def validate_return(self):
        """
        Method to validate a 'Return' transaction.
        """
        for article_entry in self.articles:
            article = frappe.get_doc("Article", article_entry.article)
            if article.status == "Available":
                frappe.throw(
              f"Article {article.name} cannot be returned without being issued first"
                )

    def validate_maximum_limit(self):
        """
        Method to validate if the member has reached the maximum limit of issued articles.
        """
        max_articles = frappe.db.get_single_value("Library Settings", "max_articles")
        count = frappe.db.count(
            "Library Transaction",
            {
                "library_member": self.library_member,
                "type": "Issue",
                "docstatus": DocStatus.submitted()
            }
        )
        if count + len(self.articles) > max_articles:
            frappe.throw("Maximum limit reached for issuing articles")

    def validate_membership(self):
        """
        Method to validate if the member has a valid membership.
        """
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": DocStatus.submitted(),
                "from_date": ("<", self.date),
                "to_date": (">", self.date),
            }
        )
        if not valid_membership:
            frappe.throw("The member does not have a valid membership")

    def before_save(self):
        """
        Method to handle actions before saving the document.
        Calculates fines for overdue, lost, and damaged articles.
        """
        if self.type == "Return":
            loan_period = frappe.db.get_single_value("Library Settings", "loan_period")
            fine_amount = frappe.db.get_single_value("Library Settings", "fine_amount")
            lost_fine = frappe.db.get_single_value("Library Settings", "lost_fine")
            damaged_fine = frappe.db.get_single_value("Library Settings", "damaged_fine")
            total_fine = 0

            issued_transactions = frappe.get_all(
                "Library Transaction",
                filters={
                    "library_member": self.library_member,
                    "type": "Issue",
                    "docstatus": DocStatus.submitted()
                },
                fields=["name", "date"]
            )

            for article_entry in self.articles:
                article_issue_date = None
                for transaction in issued_transactions:
                    articles = frappe.get_all(
                        "Add article",
                        filters={
                            "parent": transaction.name,
                            "article": article_entry.article
                        },
                        fields=["article"]
                    )
                    if articles:
                        article_issue_date = transaction.date
                        break

                article_entry.fine = 0
                if article_issue_date:
                    overdue_days = date_diff(
                        getdate(self.date), getdate(article_issue_date)
                    ) - loan_period
                    if overdue_days > 0:
                        if article_entry.fine_type == "Lost":
                            article_entry.fine = flt(
                                lost_fine + (overdue_days * fine_amount)
                            )
                        elif article_entry.fine_type == "Damaged":
                            article_entry.fine = flt(
                                damaged_fine + (overdue_days * fine_amount)
                            )
                        elif article_entry.fine_type == "No Issue":
                            article_entry.fine = flt(overdue_days * fine_amount)
                        else:
                            article_entry.fine = flt(overdue_days * fine_amount)
                    else:
                        if article_entry.fine_type == "Lost":
                            article_entry.fine = flt(lost_fine)
                        elif article_entry.fine_type == "Damaged":
                            article_entry.fine = flt(damaged_fine)
                        elif article_entry.fine_type == "No Issue":
                            article_entry.fine = 0

                    article_entry.fine = article_entry.fine or 0
                    total_fine += article_entry.fine

            self.total_amount = flt(
                total_fine + sum(article_entry.amount for article_entry in self.articles)
            )

    def validate_amount(self):
        """
        Method to validate the total amount.
        """
        if self.total_amount is None:
            self.total_amount = 0
        if self.total_amount < 0:
            frappe.throw("Total amount cannot be negative")

# @frappe.whitelist()
# def custom_query(doctype, txt, searchfield, start, page_len, filters):
#     """
#     Method to generate a custom query for fetching valid library members.
    
#     Args:
#         doctype (str): The name of the doctype to search.
#         txt (str): The search text.
#         searchfield (str): The field to search.
#         start (int): The start index of the search results.
#         page_len (int): The number of search results to return.
#         filters (dict): Additional filters for the search.
    
#     Returns:
#         list: List of valid library members.
#     """
#     today = nowdate()
#     valid_member = frappe.get_all(
#         "Library Membership",
#         filters={
#             "docstatus": 1,
#             "from_date": ("<=", today),
#             "to_date": (">=", today)
#             },
#         pluck="library_member",
#         )
#     return [[member] for member in valid_member] or []
