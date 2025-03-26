from django.template import Template, Context

# Here, we isolate the logic for template rendering

def replace_placeholders(template_string, context):
    """
    Replace placeholders in the given template string with values from context.
    
    :param template_string: The string (subject or body) with placeholders (format: {{name}})
    :param context: A dictionary of referance data for replacing the placeholders
    :return: The template string with placeholders replaced
    """
    template = Template(template_string)
    context = Context(context)
    return template.render(context)

def build_dynamic_context(user, placeholders):
    """
    Builds the context dynamically for a given user and template.
    
    Args:
        user (User): The user to build context for.
        template (EmailTemplate): The template to be used for the email.
    
    Returns:
        dict: The context with dynamic values for the user.
    """
    context = {}

    for key, value in placeholders.items():
        # The value should be an attribute or method in the User model
        context[key] = str(getattr(user, value, ''))

    return context
