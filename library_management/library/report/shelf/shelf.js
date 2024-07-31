// Copyright (c) 2024, Nandana and contributors
// For license information, please see license.txt

// frappe.query_reports["Shelf"] = {
// 	"filters": [

// 	]
// };
frappe.query_reports['Shelf'] = {
    filters: [
        {
            fieldname: 'shelf',
            label: __('Shelf'),
            fieldtype: 'Link',
            options: 'Shelf',
            
        }
        
    ]
}
