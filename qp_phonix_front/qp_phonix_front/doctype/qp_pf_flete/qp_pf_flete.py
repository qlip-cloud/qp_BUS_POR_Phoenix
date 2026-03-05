# Copyright (c) 2025, Mentum-Alphas and contributors
# For license information, please see license.txt
from qp_phonix_front.qp_phonix_front.uses_cases.flete.update_price_list import handler as update_flete_price_list

# import frappe
from frappe.model.document import Document

class qp_pf_Flete(Document):

    def on_update(self):

        update_flete_price_list()
