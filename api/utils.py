from django.db.models import Avg

def get_form_categories(form):
    """
    Returns the categories for a given form based on its type. 
    """
    
    category_map = {
        "TL": [
            "Leadership",
            "Planning and Organizing",
            "People Growth and Coaching",
            "Decision Making",
        ],
        "MANAGER": [
            "Leadership",
            "Planning and Organizing",
            "People Growth and Coaching",
            "Decision Making",
            "Problem-Solving",
            "Futuristic Imagination",
        ],
        "PM": [
            "Strategic Thinking",
            "User Empathy",
            "Decision Making",
            "Problem-Solving",
            "Business Acumen and Data Analysis",
            "Communication Skills",
        ],
    }
    return category_map.get(form.form_type, [])

