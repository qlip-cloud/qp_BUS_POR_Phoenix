import frappe

def handler():
    
    valores_flete = frappe.get_all(
        "qp_pf_Flete", fields=["name", "valor_minimo", "flete"], limit=1
    )
    
    if valores_flete:
        
        return valores_flete[0]
    
    frappe.throw(_("No hay configuración de flete disponible en qp_pf_Flete"))