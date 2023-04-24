import json

import os
import json
import frappe

@frappe.whitelist(allow_guest=True)
def handler(code):
    
    result = find_db_petition(code)
    if result:
        return {
            'statusCode': 200 if result.response else 202,
            "code": result.code ,
            "result": json.loads(result.response) if result.response else "La petición aún no se resuelve"
        }
    return {
            'statusCode': 404,
            "code": code,
            "result": "Code Not Found"
        }
    
    


def find_db_petition(code):
    if frappe.db.exists("qp_report", code):
        
        return frappe.get_doc("qp_report", code)
    
    return None

    
                       
    
    
