from .models import EmailTrigger
from .utils import send_bulk_email
from .template_helpers import replace_placeholders
from api.models import User

# Here, we isolate the emails submodule business logic

def notify_all_employees_for_new_appraisal_cycle():
    """
    This function handles the business logic of notifying all employees 
    when a new appraisal cycle starts.
    """
    # Fetch the trigger based on the event type
    try:
        trigger = EmailTrigger.objects.get(event_type="new_appraisal_cycle_started")
        template = trigger.template
        subject = template.subject
        body = template.body
    except EmailTrigger.DoesNotExist:
        raise Exception("Email trigger for new appraisal cycle does not exist.")
    
    # Fetch all employees to notify
    employees = User.objects.all()

    # Build the context for the email body (if needed, add dynamic values)
    context = {
        "employee_names": [emp.name for emp in employees],
    }

    final_body = replace_placeholders(body, context)

    recipients = [emp.email for emp in employees]
    send_bulk_email(subject, final_body, recipients)

