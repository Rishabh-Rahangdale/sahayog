import frappe
from frappe.model.document import Document

class EnquiryReminder(Document):
    def autoname(self):
        if self.case_id:
            # Count how many Enquiry Reminder records already exist for this case
            count = frappe.db.count("Enquiry Reminder", {"case_id": self.case_id}) + 1
            # Name pattern: <CaseID>-ENQREM-<count in 2 digits>
            self.name = f"{self.case_id}-ENQREM-{count:02d}"
        else:
            # Fallback autoname if case_id not provided
            self.name = frappe.model.naming.make_autoname("ENQREM-.#####")

        """Auto-fetch fields from latest Domestic Enquiry for the same case_id"""     
    def before_insert(self):
      
        if self.case_id:
            de_list = frappe.get_all(
                "Domestic Enquiry",
                filters={"case_id": self.case_id},
                order_by="creation desc",
                fields=["name", "domestic_enquiry", "status_of_response", "date_of_enquiry",
                        "place_of_enquiry", "enquiry_officer_name", ]
            )
            if de_list:
                de = de_list[0]  # latest Domestic Enquiry
                # ✅ Fetch "Yes" / "No" from Domestic Enquiry field
                self.domestic_enquiry = de.domestic_enquiry
                self.status_of_response = de.status_of_response
                self.date_of_enquiry = de.date_of_enquiry
                self.place_of_enquiry = de.place_of_enquiry
                self.enquiry_officer_name = de.enquiry_officer_name
# ✅ AUTO EMAIL ON SUBMIT (NON-BLOCKING)
    def on_submit(self):
        """
        Auto-send Enquiry Reminder email on submit using centralized utility.
        """
        try:
            from sahayog.utils.hr_utils import send_hr_workflow_email
            send_hr_workflow_email(self.name, "Enquiry Reminder", template_name="Reminder Notice of Enquiry", print_format="Reminder Notice Of Enquiry")

            frappe.msgprint(
                "Enquiry Reminder submitted successfully and email sent to employee.",
                indicator="green",
            )

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                "Enquiry Reminder Auto Email Failed on Submit",
            )


# get latest enquiry documents for a case   
@frappe.whitelist()
def check_employee_email(employee):
    emp = frappe.get_doc("Employee", employee)
    return emp.company_email if emp.company_email else None

@frappe.whitelist()
def send_reminder_enquiry_email(docname, print_format=None):
    """Send Enquiry Reminder email using centralized dynamic utility."""
    from sahayog.utils.hr_utils import send_hr_workflow_email
    return send_hr_workflow_email(docname, "Enquiry Reminder", template_name="Reminder Notice of Enquiry", print_format=print_format or "Reminder Notice Of Enquiry")
