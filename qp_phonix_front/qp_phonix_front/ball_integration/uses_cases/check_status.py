import frappe
from frappe import _


def handle(adv_int_name):

    frappe.enqueue('qp_phonix_front.scheduled_tasks.call_get_status_method', job_name=adv_int_name, adv_int_name=adv_int_name, is_async=True, timeout=21600)


def save_process_status(adv_int_name, res='Sin respuesta'):

    title = "save_process_status {}".format(adv_int_name)

    try:

        if not frappe.db.exists("qp_Adv_Int_Process_Status", adv_int_name):

            string_obj = {
                "doctype": "qp_Adv_Int_Process_Status",
                "adv_int": adv_int_name,
                "status": res
            }
            process_status_obj =  frappe.get_doc(string_obj)

            process_status_obj.insert(ignore_permissions=True)

        else:

            doc = frappe.get_doc("qp_Adv_Int_Process_Status", adv_int_name)

            doc.status = res

            doc.save(ignore_permissions=True)

    except Exception as e:

            frappe.log_error(message=frappe.get_traceback(), title=title)
            pass

    return


@frappe.whitelist()
def get_list_process_status(process_name=None):

    filter_processA = ""
    filter_processB = ""

    so_list = []

    title=_("Process Status List")

    try:

        user = frappe.session.user

        if process_name:

            sql_so_list = """
                select 'Notifying ...' as type_process, aips.adv_int, aips.status
                from tabqp_Adv_Int_Process_Status aips
                where aips.adv_int = '{p_process_name}'
                UNION ALL
                Select 'Loading ...' as type_process, name as adv_int, status
                From tabqp_Advanced_Integration
                Where name = '{p_process_name}'
            """.format(p_process_name=process_name)

        else:

            sql_so_list = """
                select 'Notifying ...' as type_process, aips.adv_int, aips.status
                from tabqp_Adv_Int_Process_Status aips
                where aips.status != 'Success' and owner = '{p_user}'
                UNION ALL
                Select 'Loading ...' as type_process, name as adv_int, status
                From tabqp_Advanced_Integration
                Where status != 'Completed' and owner = '{p_user}'
            """.format(p_user=user)

        so_list = frappe.db.sql(sql_so_list, as_dict=1)

    except Exception as error:

        so_list = []

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return so_list