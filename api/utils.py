from collections import defaultdict
from django.db.models import Avg
from api.models import Form, Question

def calculate_form_results(responses, form):
    """
    Calculate aggregated results for a form, based on assessed user.

    Args:
        responses (QuerySet): QuerySet of FormResponse objects for the form.
        form (Form): The form being processed.

    Returns:
        dict: Aggregated results including averages by question, category, and overall.
    """
    results = defaultdict(list)
    category_averages = {}
    question_averages = []
    total_sum = 0
    total_count = 0

    # Calculate averages grouped by categories
    for category in set(response.question.category for response in responses):
        category_responses = responses.filter(question__category=category)
        category_avg = category_responses.aggregate(avg=Avg("answer"))["avg"] or 0
        category_averages[category] = round(category_avg, 2)

    # Calculate per-question averages
    for question in Question.objects.filter(form=form):
        question_responses = responses.filter(question=question)
        question_avg = question_responses.aggregate(avg=Avg("answer"))["avg"] or 0
        question_averages.append({
            "id": question.id,
            "text": question.question_text,
            "average": round(question_avg, 2),
        })

        # Add to total for overall average
        total_sum += question_avg * question_responses.count()
        total_count += question_responses.count()

    # Calculate overall average
    total_average = round(total_sum / total_count, 2) if total_count > 0 else 0

    return {
        "total_average": total_average,     # float
        "categories": category_averages,    # dict
        "questions": question_averages,     # list of dicts
    }
