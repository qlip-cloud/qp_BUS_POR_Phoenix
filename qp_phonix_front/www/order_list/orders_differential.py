
import frappe
from frappe import _

from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.sales_order import get_order_differential
from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.check_status import get_list_process_status
from qp_phonix_front.resources.api.file_api import load_so
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch

from frappe.core.page.background_jobs.background_jobs import get_info

def get_context(context):

    is_guest(context)

    def callback():

        query_params = frappe.request.args

        process_name = query_params.get("process_name")
        
        context.so_differential = get_order_differential(process_name)

        print("context.so_differential", context.so_differential)

        context.process = process_name

        context.process_status_list = get_list_process_status(process_name)

        load_completed = [True if x['type_process'] == 'Loading ...' and x['status'] == 'Completed' else False for x in context.process_status_list]

        load_failed = [True if x['type_process'] == 'Loading ...' and x['status'] == 'Failed' else False for x in context.process_status_list]

        notify_completed = [True if x['type_process'] == 'Notifying ...' and x['status'] in ('Success') else False for x in context.process_status_list]

        notify_failed = [True if x['type_process'] == 'Notifying ...' and (x['status'] not in ('Starting', 'Processing', 'Success') or x['status'] in ('Stopped')) else False for x in context.process_status_list]

        enqueued_jobs = [d.get("job_name") for d in get_info()]

        # Doble verificación del proceso de notificación:
        # Desde la tabla de estado de los procesos y desde la lista de trabajos en segundo plano
        context.in_notification_process = process_name in enqueued_jobs and _("Loading Job") or ""

        # Bandera para determinar:
        # Si el proceso de carga o el proceso de notificación han terminado para detener el refrescar automático
        context.so_import_finish = (True in load_completed or True in load_failed) and 1 or 0

        # Bandera para indicar si el proceso produjo cambios en los sales orders
        context.no_changes = not context.so_differential and context.so_import_finish and _("No Changes") or ""

        context.so_notify_finish = (
            True in notify_completed or True in notify_failed or not context.in_notification_process) and 1 or 0

        # Bandera para indicar si se terminaron los procesos
        context.end_process = context.so_import_finish and not context.in_notification_process and 1 or 0

        if context.end_process and (True in notify_completed or True in notify_failed):

            context.end_process = 0

        # Bandera para indicar si se muestra el botón de confirmar
        context.show_buttom = context.end_process and True in load_completed and 1 or 0

        if context.show_buttom and (True in notify_completed or True in notify_failed):

            context.show_buttom = 0

    try_catch(callback, context)
