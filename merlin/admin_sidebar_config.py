"""
Admin sidebar navigation configuration for Django Unfold admin panel.
This configures the sidebar categories and navigation items for the admin interface.
"""


def _make_link(url_name):
    """Helper function to create a lazy link function that calls reverse at runtime."""
    def link_func(request):
        from django.urls import reverse
        try:
            return reverse(url_name)
        except Exception:
            return None
    return link_func


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
                    "link": _make_link('admin:api_note_changelist'),
                },
                {
                    "title": "جمع‌بندی‌ها",
                    "icon": "summarize",
                    "link": _make_link('admin:api_summary_changelist'),
                },
                {
                    "title": "نظرها",
                    "icon": "comment",
                    "link": _make_link('admin:api_comment_changelist'),
                },
                {
                    "title": "کاربران",
                    "icon": "person",
                    "link": _make_link('admin:api_user_changelist'),
                },
                {
                    "title": "دسترسی‌ها",
                    "icon": "lock",
                    "link": _make_link('admin:api_noteuseraccess_changelist'),
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
                    "link": _make_link('admin:api_apikey_changelist'),
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
                    "link": _make_link('admin:api_cycle_changelist'),
                },
                {
                    "title": "تیم‌ها",
                    "icon": "group",
                    "link": _make_link('admin:api_team_changelist'),
                },
                {
                    "title": "دپارتمان‌ها",
                    "icon": "business",
                    "link": _make_link('admin:api_department_changelist'),
                },
                {
                    "title": "سازمان‌ها",
                    "icon": "apartment",
                    "link": _make_link('admin:api_organization_changelist'),
                },
                {
                    "title": "قبیله‌ها",
                    "icon": "workspaces",
                    "link": _make_link('admin:api_tribe_changelist'),
                },
                {
                    "title": "نقش‌ها",
                    "icon": "badge",
                    "link": _make_link('admin:api_role_changelist'),
                },
                {
                    "title": "چپترها",
                    "icon": "menu_book",
                    "link": _make_link('admin:api_chapter_changelist'),
                },
                {
                    "title": "کمیته‌ها",
                    "icon": "groups",
                    "link": _make_link('admin:api_committee_changelist'),
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
                    "link": _make_link('admin:api_feedback_changelist'),
                },
                {
                    "title": "درخواست‌های بازخورد",
                    "icon": "request_quote",
                    "link": _make_link('admin:api_feedbackrequest_changelist'),
                },
                {
                    "title": "فرم‌های بازخورد",
                    "icon": "description",
                    "link": _make_link('admin:api_feedbackform_changelist'),
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
                    "link": _make_link('admin:api_form_changelist'),
                },
                {
                    "title": "سوال‌ها",
                    "icon": "help",
                    "link": _make_link('admin:api_question_changelist'),
                },
                {
                    "title": "پاسخ‌ها",
                    "icon": "reply",
                    "link": _make_link('admin:api_formresponse_changelist'),
                },
                {
                    "title": "Form assignments",
                    "icon": "assignment_ind",
                    "link": _make_link('admin:api_formassignment_changelist'),
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
                    "link": _make_link('admin:api_orgassignmentsnapshot_changelist'),
                },
                {
                    "title": "اسنپ‌شات‌های جبران خدمات",
                    "icon": "payments",
                    "link": _make_link('admin:api_compensationsnapshot_changelist'),
                },
                {
                    "title": "اسنپ‌شات‌های سطح فنی",
                    "icon": "trending_up",
                    "link": _make_link('admin:api_senioritysnapshot_changelist'),
                },
                {
                    "title": "پله‌های حقوقی",
                    "icon": "stairs",
                    "link": _make_link('admin:api_payband_changelist'),
                },
                {
                    "title": "Data Access Override",
                    "icon": "admin_panel_settings",
                    "link": _make_link('admin:api_dataaccessoverride_changelist'),
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
                    "link": _make_link('admin:api_valuetag_changelist'),
                },
                {
                    "title": "Organization Behaviour Tags",
                    "icon": "loyalty",
                    "link": _make_link('admin:api_orgvaluetag_changelist'),
                },
            ],
        },
    ],
}

