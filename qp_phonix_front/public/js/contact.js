frappe.ui.form.on('Contact', {
  
  onload: function(frm) {
    if (frm.is_new()) {
      frm.set_value('qp_is_recipient', 1);
    }
  }

});