# Copyright (c) 2026, Developer Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExParteEnquiry(Document):
	def before_insert(self):
		self._validate_ua_response()

	def validate(self):
		self._validate_ua_response()

	def _latest_ua_response(self):
		if not self.case_id:
			return None

		latest_ua = frappe.get_all(
			"Unauthorized Absence",
			filters={"case_id": self.case_id},
			fields=["response_of_ua"],
			order_by="creation desc",
			limit_page_length=1,
		)

		if not latest_ua:
			return None

		return latest_ua[0].get("response_of_ua")

	def _validate_ua_response(self):
		if self._latest_ua_response() == "Satisfactory":
			frappe.throw(
				"Ex Parte Enquiry cannot be created because the linked Unauthorized Absence has Status of Response set to Satisfactory."
			)

	def autoname(self):
		"""Generate structured name based on Case ID"""
		if self.case_id:
			# Count ex parte enquiries for same case
			count = frappe.db.count("Ex Parte Enquiry", {"case_id": self.case_id}) + 1
			self.name = f"{self.case_id}-EXP-{count:02d}"
		else:
			# fallback autoname if no case linked
			self.name = frappe.model.naming.make_autoname("EXP-.#####")

	def on_submit(self):
		"""
		Auto-send Ex Parte Enquiry email on submit using centralized utility.
		"""
		try:
			from sahayog.utils.hr_utils import send_hr_workflow_email
			# Explicitly specifying print format
			send_hr_workflow_email(self.name, "Ex Parte Enquiry", print_format="Ex Parte Enquiry")

			frappe.msgprint(
				"Ex Parte Enquiry submitted successfully and email sent to employee.",
				indicator="green"
			)

		except Exception:
			# Never block submit
			frappe.log_error(
				frappe.get_traceback(),
				"Auto Ex Parte Enquiry Email Failed on Submit"
			)

@frappe.whitelist()
def check_employee_email(employee):
	"""Return employee's email if exists, otherwise None."""
	emp = frappe.get_doc("Employee", employee)
	return emp.company_email if emp.company_email else None

@frappe.whitelist()
def send_ex_parte_enquiry_email(docname):
	"""Send Ex Parte Enquiry Email using centralized dynamic utility."""
	from sahayog.utils.hr_utils import send_hr_workflow_email
	return send_hr_workflow_email(docname, "Ex Parte Enquiry", print_format="Ex Parte Enquiry")

