"""
Admin sidebar navigation configuration for Django Unfold admin panel.
This configures the sidebar categories and navigation items for the admin interface.
"""
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
                    "model": "api.note",
                },
                {
                    "title": "نظرها",
                    "icon": "comment",
                    "model": "api.comment",
                },
                {
                    "title": "کاربران",
                    "icon": "person",
                    "model": "api.user",
                },
                {
                    "title": "دسترسی‌ها",
                    "icon": "lock",
                    "model": "api.noteuseraccess",
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
                    "model": "api.apikey",
                },
            ],
        },
        {
            "title": "Organization",
            "separator": True,
            "items": [
                {
                    "title": "Cycles",
                    "icon": "event",  # Changed from "calendar" to "event"
                    "model": "api.cycle",
                },
                {
                    "title": "تیم‌ها",
                    "icon": "group",
                    "model": "api.team",
                },
                {
                    "title": "دپارتمان‌ها",
                    "icon": "business",
                    "model": "api.department",
                },
                {
                    "title": "سازمان‌ها",
                    "icon": "apartment",
                    "model": "api.organization",
                },
                {
                    "title": "قبیله‌ها",
                    "icon": "workspaces",
                    "model": "api.tribe",
                },
                {
                    "title": "نقش‌ها",
                    "icon": "badge",
                    "model": "api.role",
                },
                {
                    "title": "چپترها",
                    "icon": "menu_book",
                    "model": "api.chapter",
                },
                {
                    "title": "کمیته‌ها",
                    "icon": "groups",
                    "model": "api.committee",
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
                    "model": "api.feedback",
                },
                {
                    "title": "درخواست‌های بازخورد",
                    "icon": "request_quote",
                    "model": "api.feedbackrequest",
                },
                {
                    "title": "فرم‌های بازخورد",
                    "icon": "description",
                    "model": "api.feedbackform",
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
                    "model": "api.form",
                },
                {
                    "title": "سوال‌ها",
                    "icon": "help",
                    "model": "api.question",
                },
                {
                    "title": "پاسخ‌ها",
                    "icon": "reply",
                    "model": "api.formresponse",
                },
                {
                    "title": "Form assignments",
                    "icon": "assignment_ind",
                    "model": "api.formassignment",
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
                    "model": "api.orgassignmentsnapshot",
                },
                {
                    "title": "اسنپ‌شات‌های جبران خدمات",
                    "icon": "payments",
                    "model": "api.compensationsnapshot",
                },
                {
                    "title": "اسنپ‌شات‌های سطح فنی",
                    "icon": "trending_up",
                    "model": "api.senioritysnapshot",
                },
                {
                    "title": "پله‌های حقوقی",
                    "icon": "stairs",
                    "model": "api.payband",
                },
                {
                    "title": "Data Access Override",
                    "icon": "admin_panel_settings",
                    "model": "api.dataaccessoverride",
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
                    "model": "api.valuetag",
                },
                {
                    "title": "Organization Behaviour Tags",
                    "icon": "loyalty",
                    "model": "api.orgvaluetag",
                },
            ],
        },
    ],
}

