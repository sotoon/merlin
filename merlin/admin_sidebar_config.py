"""
Admin sidebar navigation configuration for Django Unfold admin panel.
This configures the sidebar categories and navigation items for the admin interface.
"""
from django.urls import reverse


def get_admin_url(model_path):
    """Helper function to generate admin changelist URL for a model."""
    app_label, model_name = model_path.split('.')
    try:
        return reverse(f'admin:{app_label}_{model_name}_changelist')
    except Exception:
        return None


UNFOLD_SIDEBAR_CONFIG = {
    "show_search": True,
    "show_all_applications": False,
    "navigation": [
        {
            "title": "Core",
            "separator": True,
            "items": [
                {
                    "title": "یادداشت‌ها",
                    "icon": "note",
                    "link": lambda request: reverse('admin:api_note_changelist'),
                },
                {
                    "title": "نظرها",
                    "icon": "comment",
                    "link": lambda request: reverse('admin:api_comment_changelist'),
                },
                {
                    "title": "کاربران",
                    "icon": "person",
                    "link": lambda request: reverse('admin:api_user_changelist'),
                },
                {
                    "title": "دسترسی‌ها",
                    "icon": "lock",
                    "link": lambda request: reverse('admin:api_noteuseraccess_changelist'),
                },
            ],
        },
        {
            "title": "Integration",
            "separator": True,
            "items": [
                {
                    "title": "API Keys",
                    "icon": "key",
                    "link": lambda request: reverse('admin:api_apikey_changelist'),
                },
            ],
        },
        {
            "title": "Organization",
            "separator": True,
            "items": [
                {
                    "title": "Cycles",
                    "icon": "event",
                    "link": lambda request: reverse('admin:api_cycle_changelist'),
                },
                {
                    "title": "تیم‌ها",
                    "icon": "group",
                    "link": lambda request: reverse('admin:api_team_changelist'),
                },
                {
                    "title": "دپارتمان‌ها",
                    "icon": "business",
                    "link": lambda request: reverse('admin:api_department_changelist'),
                },
                {
                    "title": "سازمان‌ها",
                    "icon": "apartment",
                    "link": lambda request: reverse('admin:api_organization_changelist'),
                },
                {
                    "title": "قبیله‌ها",
                    "icon": "workspaces",
                    "link": lambda request: reverse('admin:api_tribe_changelist'),
                },
                {
                    "title": "نقش‌ها",
                    "icon": "badge",
                    "link": lambda request: reverse('admin:api_role_changelist'),
                },
                {
                    "title": "چپترها",
                    "icon": "menu_book",
                    "link": lambda request: reverse('admin:api_chapter_changelist'),
                },
                {
                    "title": "کمیته‌ها",
                    "icon": "groups",
                    "link": lambda request: reverse('admin:api_committee_changelist'),
                },
            ],
        },
        {
            "title": "Feedback",
            "separator": True,
            "items": [
                {
                    "title": "بازخوردها",
                    "icon": "feedback",
                    "link": lambda request: reverse('admin:api_feedback_changelist'),
                },
                {
                    "title": "درخواست‌های بازخورد",
                    "icon": "request_quote",
                    "link": lambda request: reverse('admin:api_feedbackrequest_changelist'),
                },
                {
                    "title": "فرم‌های بازخورد",
                    "icon": "description",
                    "link": lambda request: reverse('admin:api_feedbackform_changelist'),
                },
            ],
        },
        {
            "title": "Form",
            "separator": True,
            "items": [
                {
                    "title": "فرم‌ها",
                    "icon": "assignment",
                    "link": lambda request: reverse('admin:api_form_changelist'),
                },
                {
                    "title": "سوال‌ها",
                    "icon": "help",
                    "link": lambda request: reverse('admin:api_question_changelist'),
                },
                {
                    "title": "پاسخ‌ها",
                    "icon": "reply",
                    "link": lambda request: reverse('admin:api_formresponse_changelist'),
                },
                {
                    "title": "Form assignments",
                    "icon": "assignment_ind",
                    "link": lambda request: reverse('admin:api_formassignment_changelist'),
                },
            ],
        },
        {
            "title": "Performance Table",
            "separator": True,
            "items": [
                {
                    "title": "اسنپ‌شات‌های انتساب سازمانی",
                    "icon": "account_tree",
                    "link": lambda request: reverse('admin:api_orgassignmentsnapshot_changelist'),
                },
                {
                    "title": "اسنپ‌شات‌های جبران خدمات",
                    "icon": "payments",
                    "link": lambda request: reverse('admin:api_compensationsnapshot_changelist'),
                },
                {
                    "title": "اسنپ‌شات‌های سطح فنی",
                    "icon": "trending_up",
                    "link": lambda request: reverse('admin:api_senioritysnapshot_changelist'),
                },
                {
                    "title": "پله‌های حقوقی",
                    "icon": "stairs",
                    "link": lambda request: reverse('admin:api_payband_changelist'),
                },
                {
                    "title": "Data Access Override",
                    "icon": "admin_panel_settings",
                    "link": lambda request: reverse('admin:api_dataaccessoverride_changelist'),
                },
            ],
        },
        {
            "title": "Tags",
            "separator": True,
            "items": [
                {
                    "title": "Behaviour Tags",
                    "icon": "label",
                    "link": lambda request: reverse('admin:api_valuetag_changelist'),
                },
                {
                    "title": "Organization Behaviour Tags",
                    "icon": "loyalty",
                    "link": lambda request: reverse('admin:api_orgvaluetag_changelist'),
                },
            ],
        },
    ],
}

