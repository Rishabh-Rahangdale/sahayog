import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import formatdate
class SuspensionProcess(Document):
    def autoname(self):
        """Generate structured name based on linked Disciplinary Case"""
        if self.case_id:
            count = frappe.db.count("Suspension Process", {"case_id": self.case_id}) + 1
            self.name = f"{self.case_id}-SUSP-{count:02d}"
        else:
            # fallback if case_id not linked
            self.name = frappe.model.naming.make_autoname("SUSP-.#####")

    def before_insert(self):
        """Restrict record creation if Suspension Required = No in parent case"""
        if self.case_id:
            case = frappe.get_doc("Disciplinary Case", self.case_id)
            if case.suspension_required == "No":
                frappe.throw(
                    _("You cannot create a Suspension Process because 'Suspension Required' is set to No in the linked Disciplinary Case."),
                    title=_("Action Restricted")
                )

    def validate(self):
        """Extra safety — block save if parent says No"""
        if self.case_id:
            case = frappe.get_doc("Disciplinary Case", self.case_id)
            if case.suspension_required == "No":
                frappe.throw(
                    _("Suspension Required is set to No in the linked Disciplinary Case. You cannot create or save this record."),
                    title=_("Validation Failed")
                )

# ✅ ONLY ADDITION — existing logic untouched
    def on_submit(self):
        """
        Auto-send Suspension email on submit using centralized utility.
        """
        try:
            from sahayog.utils.hr_utils import send_hr_workflow_email
            send_hr_workflow_email(self.name, "Suspension Process", print_format="Suspension Order")

            frappe.msgprint(
                "Suspension Process submitted successfully and email sent to employee.",
                indicator="green"
            )

        except Exception:
            # Never block submit
            frappe.log_error(
                frappe.get_traceback(),
                "Auto Suspension Email Failed on Submit"
            )
            
@frappe.whitelist()
def check_employee_email(employee):
    emp = frappe.get_doc("Employee", employee)
    return emp.company_email if emp.company_email else None

@frappe.whitelist()
def save_and_send_email(employee, email, docname):
    emp = frappe.get_doc("Employee", employee)
    emp.company_email = email
    emp.save(ignore_permissions=True)
    send_suspension_email(docname)
    return "OK"

@frappe.whitelist()
def send_suspension_email(docname):
    """Send Suspension email using centralized dynamic utility."""
    from sahayog.utils.hr_utils import send_hr_workflow_email
    return send_hr_workflow_email(docname, "Suspension Process", print_format="Suspension Order")
