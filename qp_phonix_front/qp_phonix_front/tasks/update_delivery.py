import json
import frappe
from datetime import datetime
from frappe.utils import get_url, getdate,today
from gp_phonix_integration.gp_phonix_integration.service.connection import execute_send
from gp_phonix_integration.gp_phonix_integration.constant.api_setup import ORDER


@frappe.whitelist()
def all():
    
    sales_names = frappe.db.get_list("Sales Order", 
                                    filters = {
                                         "status": "To Deliver and Bill", 
                                         #"delivery_date":[">=", today()],
                                         "name":"SAL-ORD-2023-00138",
                                         "qp_phonix_reference": ["IS", "set"]
                                    }, pluck='name')
    
    for sale_names in sales_names:
        
        sale_order = frappe.get_doc("Sales Order", sale_names)
        
        update_delivery_data(sale_order)
    
    frappe.db.commit()
           
def only(sale_order):

    update_delivery_data(sale_order)
    
    frappe.db.commit()
    
def update_delivery_data(sale_order):
    is_change = False
    if (sale_order.qp_phonix_reference):
        
        so_respose = get_order_delivery_data(sale_order.qp_phonix_reference)

        if so_respose.get("ReturnCode") == "SUCCESS":
            
            for item in sale_order.items:
                
                for line in so_respose.get("ReturnJson").get("Lines"):
                    
                    if line.get("Id") == item.item_code and line.get("LineNumber") == item.line_number and (item.delivery_date != getdate(line.get("RequestDate")) or item.qp_phoenix_status != getdate(line.get("Status"))):

                        item.delivery_date = getdate(line.get("RequestDate")) if line.get("RequestDate") != '1900-01-01' else datetime.strptime(today(), "%Y-%m-%d").date()
                        
                        item.qp_phoenix_status = line.get("Status")

                        item.delivery_date_visible = True if line.get("RequestDate") != '1900-01-01' else False

                        item.save()
                        
                        if sale_order.delivery_date < item.delivery_date:
                            is_change = True
                            sale_order.delivery_date = item.delivery_date
            
            if is_change:
                
                update_delivery_log = frappe.get_doc({
                        'doctype': "qp_pf_UpdateDeliveryLog",
                        'sales_order': sale_order.name})
                                
                update_delivery_log.insert()
                
                sale_order.save()
                        
def get_order_delivery_data(qp_phonix_reference):
    
    payload = json.dumps({"IdOrder": qp_phonix_reference})

    company = frappe.defaults.get_user_default("company")

    return execute_send(company_name=company, endpoint_code=ORDER, json_data=payload)