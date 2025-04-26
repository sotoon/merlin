from collections import defaultdict
from django.db.models import Avg
from api.models import Question


__all__ = ['calculate_form_results']


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
    category_counts = {}    # This is for keeping the number of assessing users
    total_sum = 0
    total_count = 0

    # Calculate averages grouped by categories
    for category in set(response.question.category for response in responses):
        category_responses = responses.filter(question__category=category)
        category_avg = category_responses.aggregate(avg=Avg("answer"))["avg"]

        category_averages[category] = category_avg
        category_counts[category] = category_responses.count()

    # Calculate per-question averages
    for question in Question.objects.filter(form=form):
        question_responses = responses.filter(question_id=question.id)
        question_avg = question_responses.aggregate(avg=Avg("answer"))["avg"]

        question_averages.append({
            "id": question.id,
            "text": question.question_text,
            "average": question_avg,
            "count": question_responses.count()
        })

        # Add to total for overall average
        total_sum += (question_avg if question_avg is not None else 0) * question_responses.count()
        total_count += question_responses.count()

    # Calculate overall average, passing None if there's no data
    total_average = None if total_count == 0 else total_sum / total_count

    return {
        "total_average": total_average,     # float
        "categories": category_averages,    # dict
        "questions": question_averages,     # list of dicts
        "category_counts": category_counts, # list of integers
        "questions": question_averages,     # list of integers
    }
