import frappe


def show_global_parameters():

	if frappe.db.get_value("User", frappe.session.user, "user_type") == "Website User":
		return True

	return False


def set_default(login_manager):

    set_global_default()

    return True


def clear_default(login_manager):

    if show_global_parameters():
        frappe.local.cookie_manager.delete_cookie("ball_company")
        frappe.local.cookie_manager.delete_cookie("ball_customer_id")
        frappe.local.cookie_manager.delete_cookie("ball_customer_name")

    return True

@frappe.whitelist()
def set_global_default(ball_company="", ball_customer_id="", ball_customer_name=""):

    print("***************set_global_default****************")

    if show_global_parameters():
        if hasattr(frappe.local, "cookie_manager"):
            frappe.local.cookie_manager.set_cookie("ball_company", ball_company)
            frappe.local.cookie_manager.set_cookie("ball_customer_id", ball_customer_id)
            frappe.local.cookie_manager.set_cookie("ball_customer_name", ball_customer_name)

    return True


