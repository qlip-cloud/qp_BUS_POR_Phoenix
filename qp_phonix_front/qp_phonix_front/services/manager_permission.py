import frappe

def handler():
    
    email = frappe.session.user

    sql = """
    SELECT
        role.role_code
    FROM
        tabUser as user
    inner join
        tabqp_pf_ProfileRole as profile_role
        on (user.role_profile_name = profile_role.profile_name)
    inner join tabqp_pf_HasRole as has_role
        on (profile_role.profile_name = has_role.parent)
    inner join tabqp_pf_Rol as role
        on (has_role.role = role.name)
    where user.name = '{email}'
    """.format(email = email)

    permission_format = {}
    
    permissions =  frappe.db.sql(sql, as_dict = 1)

    if not permissions:

        frappe.throw("Este usuario no tiene un Perfil valido")

    all_permission = frappe.get_list("qp_pf_Rol",fields = ["role_code"])

    for permission in all_permission:

        permission_format.setdefault(permission.get("role_code"), True if permission in  permissions else False)

    return permission_format