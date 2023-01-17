import frappe

def handler(callback, context):

    try:
    
        callback()

    except Exception as error:
        
        traceback = frappe.get_traceback()
        frappe.log_error(message=traceback, title = "Render action")
        print(traceback)
        context.has_error = True