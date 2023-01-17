import frappe
from frappe import _
import requests
import json
from gp_phonix_integration.gp_phonix_integration.service.connection import execute_send
from gp_phonix_integration.gp_phonix_integration.constant.api_setup import CHECKOUTART

from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import __get_uom_list

MSG_ERROR_INI = _("<b>At this time we do not have the necessary inventory for:<br></b><ol>")

MSG_ERROR = _("<li>Product {}. At this time we have the amount of {}.</li>")

MSG_ERROR_FINAL = _("</ol><br><b>Please make the necessary changes before continuing with the confirmation of your purchase.</b>")

def send_check_out_so(sales_order):

    res = {'name': '', 'msg': 'Fail', 'result': 400, 'body_data': '', 'response': ''}

    title = _("Check Out Sales Order")

    art_json = None

    so_respose = None

    try:

        company = frappe.defaults.get_user_default("company")

        art_json = __prepare_petition(sales_order)

        res['body_data'] = art_json

        so_respose = execute_send(company_name=company, endpoint_code=CHECKOUTART, json_data=art_json)

        res['response'] = so_respose

        if so_respose.get("Error") and so_respose.get("Error").get("Estado") == "Exitoso":

            # verificar existencias y devolver resultado

            so_obj = frappe.get_doc("Sales Order", sales_order)

            checkoutart_list = []

            for item_gp in so_respose.get("Articulos"):

                item_code = item_gp.get("IdArticulo")

                item_obj = next(x for x in so_obj.items if x.item_code == item_code)

                qty_gp = float(item_gp.get("CantidadArt"))

                item_type_gp = int(item_gp.get("ItemType"))

                if item_type_gp == 1 and qty_gp < float(item_obj.get("qty")):

                    # Determinar multiplos próximo para armar el mensaje del resultado

                    conversion_factor = __get_conversion_factor(item_code)

                    multi_qty = __round_down(qty_gp, conversion_factor)

                    multi_qty = multi_qty if multi_qty > 0 else 0

                    # TODO: concatenar checkoutart_list

                    checkoutart_list.append(
                        {
                            "item_name": item_obj.get("item_name"),
                            "multi_qty": multi_qty,
                            "qty": item_obj.get("qty"),
                            "qty_gp": qty_gp
                        }
                    )

            if not checkoutart_list:

                res['name'] = sales_order

                res['msg'] = 'Success'

                res['result'] = 200

            else:

                res['result'] = 400

                res['name'] = sales_order

                msg_str = _(MSG_ERROR_INI)

                details_list = []

                for row in checkoutart_list:

                    msg_str = msg_str + _(MSG_ERROR).format(row.get("item_name"), row.get("multi_qty")) 

                    details_list.append(
                        {
                            "customer": so_obj.get("customer"),
                            "customer_name": so_obj.get("customer_name"),
                            "item_name": row.get("item_name"),
                            "qty": row.get("qty"),
                            "qty_gp": row.get("qty_gp"),
                            "sales_order": sales_order
                        }
                    )

                res['msg'] = msg_str + _(MSG_ERROR_FINAL)

                res['details'] = details_list

            return res

        else:

            frappe.log_error(message='\n'.join((str(art_json), str(so_respose))), title=_("Call Check Out GP"))

    except Exception as error:

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return res


def __prepare_petition(sales_order):

    art_json = {}

    so_obj = frappe.get_doc("Sales Order", sales_order)

    art_body = []

    bdga_body = []

    art_bdga = []

    for item in so_obj.items:

        art_body.append(__todict("Id", item.item_code))

        art_bdga.append(item.item_group)

    art_json['Articulos'] = art_body

    bdgas = [x for x in list(set(art_bdga))]

    for bdga in bdgas:

        bdga_body.append(__todict("Id", bdga))

    art_json['Bodegas'] = bdga_body

    return json.dumps(art_json)


def __todict(param_key, param_value):

    obj_value = {
        param_key: param_value,
    }

    return  obj_value


def __get_conversion_factor(item_code):

    uom_list = __get_uom_list(item_code)

    return uom_list and int(uom_list[0]['conversion_factor']) or 1


def __round_down(num, divisor):
    
    return num - (num%divisor)
