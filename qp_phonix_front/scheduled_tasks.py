import frappe, time


from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.check_status import save_process_status
from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.sales_order import send_to_gp_sales_order_by_batch


def call_get_status_method(adv_int_name):
    #print("***************se llamó*********************", adv_int_name)

    title = "call_get_status_method {}".format(adv_int_name)

    res = {'name': adv_int_name, 'msg': 'exceeded', 'result': 400, 'list_ok': [], 'list_error':[]}

    max_retries = 720 # 20 # 10800 # TODO: configurar max_retries

    save_process_status(adv_int_name, 'Processing')

    for x in range(0, max_retries):
        try:

            adv_int_status = frappe.get_value('qp_Advanced_Integration', adv_int_name, ['status'])
            if adv_int_status:
                if adv_int_status == "Completed":
                    # Enviar notificación a GP
                    #print("notificar")
                    res = send_to_gp_sales_order_by_batch(adv_int_name)
                    break
                elif adv_int_status == "Active" or adv_int_status == "Starting":
                    delay = 15 # 60
                    time.sleep(delay)
                    #print("esperar")
                    continue
                elif adv_int_status == "Failed":
                    res['msg'] = 'failed'
                    #print("romper bucle - failed")
                    break
            else:
                res['msg'] = 'no_recordset'
                #print("romper bucle - no hay registro")
                break

        except Exception as e:

            res['msg'] = 'error'
            frappe.log_error(message=frappe.get_traceback(), title=title)
            pass

    save_process_status(adv_int_name, res.get('msg'))
    #print("call_get_status_method result ---->",res)
    return res
