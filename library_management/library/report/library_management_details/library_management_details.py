from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    """
    Generates a report with library member details including membership status, period, and current articles.
    
    Args:
        filters (dict, optional): Dictionary containing filter values for the report.
    
    Returns:
        columns (list): List of dictionaries defining the columns of the report.
        data (list): List of dictionaries containing the member data for the report.
    """
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
            'label': _('Membership From'),
            'fieldtype': 'Date',
        },
        {
            'fieldname': 'to_date',
            'label': _('Membership To'),
            'fieldtype': 'Date',
        },
        {
            'fieldname': 'membership_status',
            'label': _('Membership Status'),
            'fieldtype': 'Data',
            'width': 150
        },
        {
            'fieldname': 'current_articles',
            'label': _('Current Articles Held'),
            'fieldtype': 'Data',
            'width': 250
        },
    ]

    today = frappe.utils.nowdate()

    query = """
    SELECT
        lm.fullname,
        lm.email_address,
        lm.phone,
        lm.name AS member_name,
        IF(membership.from_date IS NOT NULL, membership.from_date, NULL) AS from_date,
        IF(membership.to_date IS NOT NULL, membership.to_date, NULL) AS to_date,
        IF(membership.from_date IS NOT NULL, 'Valid Membership', 'No Membership') 
        AS membership_status,
        GROUP_CONCAT(DISTINCT current_articles.article_name 
        ORDER BY current_articles.article_name SEPARATOR ', ') AS current_articles
    FROM
        `tabLibrary Member` lm
    LEFT JOIN (
        SELECT
            lmem.library_member,
            lmem.from_date,
            lmem.to_date
        FROM
            `tabLibrary Membership` lmem
        WHERE
            lmem.docstatus = 1
            AND lmem.from_date <= %(today)s
            AND lmem.to_date >= %(today)s
        ORDER BY
            lmem.from_date DESC
    ) membership ON lm.name = membership.library_member
    LEFT JOIN (
        SELECT
            lt.library_member,
            la.article AS article_name
        FROM
            `tabLibrary Transaction` lt
        JOIN
            `tabAdd article` la ON lt.name = la.parent
        LEFT JOIN (
            SELECT
                library_member,
                article,
                MAX(date) AS last_return_date
            FROM
                `tabLibrary Transaction`
            WHERE
                type = 'Return'
                AND docstatus = 1
            GROUP BY
                library_member, article
        ) returns ON returns.library_member = lt.library_member 
        AND returns.article = la.article
        WHERE
            lt.type = 'Issue'
            AND lt.docstatus = 1
            AND (returns.last_return_date IS NULL OR lt.date > returns.last_return_date)
    ) current_articles ON lm.name = current_articles.library_member
    GROUP BY
        lm.fullname, lm.email_address, lm.phone, lm.name, from_date, to_date,
        membership_status
    """

    data = frappe.db.sql(query, {"today": today}, as_dict=True)

    return columns, data
