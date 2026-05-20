// Copyright (c) 2026, Mentum-Alphas and contributors
// For license information, please see license.txt

frappe.ui.form.on('qp_PF_Send_Emails', {
	 refresh(frm) {
        frm.add_custom_button('Enviar Correos', () => {
            frappe.call({
                method: 'qp_phonix_front.qp_phonix_front.doctype.qp_pf_send_emails.qp_pf_send_emails.send_mass_emails',
                args: {
                    docname: frm.doc.name
                },
                callback: function(r) {
                    frappe.msgprint('Proceso completado');
                }
            });
        });
    },
    setup(frm){
        frm.set_query('sales_order', 'sales_orders', function() {
            return {
                filters: {
                    docstatus: 1
                }
            };
        });
    }
});
