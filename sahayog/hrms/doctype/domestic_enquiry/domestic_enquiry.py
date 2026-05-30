import frappe
from frappe.model.document import Document

class DomesticEnquiry(Document):
    def autoname(self):
        if self.case_id:
            count = frappe.db.count("Domestic Enquiry", {"case_id": self.case_id}) + 1
            self.name = f"{self.case_id}-ENQ-{count:02d}"
        else:
            self.name = frappe.model.naming.make_autoname("ENQ-.#####")

    def validate(self):
        """Restrict creation if linked Response to SCN is Satisfactory"""
        if self.case_id:
            status = frappe.db.get_value(
                "Response to SCN",
                {"case_id": self.case_id},
                "status_of_response"
            )
            if status == "Satisfactory":
                frappe.throw(
                    ("Cannot create Domestic Enquiry when 'Status of Response' is 'Satisfactory'."),
                    title=("Action Restricted")
                )

# ✅ ONLY ADDITION
    def on_submit(self):
        """
        Auto-send Domestic Enquiry email on submit using centralized utility.
        """
        try:
            from sahayog.utils.hr_utils import send_hr_workflow_email
            send_hr_workflow_email(self.name, "Domestic Enquiry", template_name="Domestic Enquiry Notice", print_format="Domestic Enquiry")

            frappe.msgprint(
                "Domestic Enquiry submitted successfully and notice email sent to employee.",
                indicator="green"
            )

        except Exception:
            # Never block submit
            frappe.log_error(
                frappe.get_traceback(),
                "Auto Domestic Enquiry Email Failed on Submit"
            )


# Check employee email
@frappe.whitelist()
def check_employee_email(employee):
    emp = frappe.get_doc("Employee", employee)
    return emp.company_email if emp.company_email else None

# Send Domestic Enquiry Notice Email
@frappe.whitelist()
def send_domestic_enquiry_email(docname):
    """Send Domestic Enquiry Notice Email using centralized dynamic utility."""
    from sahayog.utils.hr_utils import send_hr_workflow_email
    return send_hr_workflow_email(docname, "Domestic Enquiry", template_name="Domestic Enquiry Notice", print_format="Domestic Enquiry")
