// Copyright (c) 2021, Mentum-Alphas and contributors
// For license information, please see license.txt

frappe.ui.form.on('qp_vf_ItemGroup', {
	// refresh: function(frm) {

	// }

	onload: function(frm) {

		var res = item_attr_list(frm);

	}
});

function item_attr_list(frm){

	let item_attr = []

	frappe.call({
		async: false,
		method:'qp_phonix_front.qp_phonix_front.uses_cases.item_group.item_group_list.vf_item_attr_list',
		callback: function(r) {
			item_attr = r.message;
			var df = frappe.meta.get_docfield("qp_vf_ItemGroupFilter","item_attribute", frm.doc.name);
			df.options =  item_attr;
			return item_attr;
		}
	});

}
