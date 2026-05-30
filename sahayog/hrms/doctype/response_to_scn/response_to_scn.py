from frappe.model.document import Document
import frappe
import frappe
from frappe.utils import formatdate
from frappe import _

class ResponsetoSCN(Document):

    def autoname(self):
        if self.case_id:
            count = frappe.db.count("Response to SCN", {"case_id": self.case_id}) + 1
            self.name = f"{self.case_id}-RSCN-{count:02d}"
        else:
            self.name = frappe.model.naming.make_autoname("RSCN-.#####")

# ✅ AUTO EMAIL ON SUBMIT (NON-BLOCKING)
    def on_submit(self):
        """
        Auto-send Response to SCN email on submit using centralized utility.
        """
        try:
            from sahayog.utils.hr_utils import send_hr_workflow_email
            send_hr_workflow_email(self.name, "Response to SCN")

            frappe.msgprint(
                "Response to SCN submitted successfully and email sent to employee.",
                indicator="green"
            )

        except Exception:
            # Never block submit
            frappe.log_error(
                frappe.get_traceback(),
                "Response to SCN Auto Email Failed on Submit"
            )


@frappe.whitelist()
def check_employee_email(employee):
    emp = frappe.get_doc("Employee", employee)
    return emp.company_email if emp.company_email else None

@frappe.whitelist()
def send_response_scn_email(docname):
    """Send Response to SCN email using centralized dynamic utility."""
    from sahayog.utils.hr_utils import send_hr_workflow_email
    return send_hr_workflow_email(docname, "Response to SCN")
