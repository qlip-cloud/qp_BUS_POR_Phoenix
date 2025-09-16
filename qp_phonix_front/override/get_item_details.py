import frappe
import json
from erpnext.stock.get_item_details import get_item_details as erpnext_get_item_details # type: ignore

@frappe.whitelist()
def get_item_details(args, doc=None, for_validate=False, overwrite_warehouse=True):


  erpnext_data = erpnext_get_item_details(args, doc, for_validate, overwrite_warehouse)

  if isinstance(args, str):
    args = json.loads(args)
  
  if args.get("doctype") != "Quotation":
    return erpnext_data

  item = frappe.get_doc("Item", args.get("item_code"))
  price_group = item.get("qp_price_group")

  customer = args.get("customer")
  idlevel = frappe.db.get_value("Customer", customer, "customer_group") if customer else None

  if price_group and idlevel:
    gp_level = frappe.db.get_value("qp_GP_Level", {"group_type": price_group, "idlevel": idlevel}, ["discountpercentage"], as_dict=True)
    if gp_level and gp_level.discountpercentage:
      discount_percentage = gp_level.discountpercentage
      price_list_rate = erpnext_data.get("price_list_rate", 0)
      discounted_price = price_list_rate - (price_list_rate * discount_percentage / 100)
      erpnext_data["discount_percentage"] = discount_percentage

  return erpnext_data
    

