# flake8: noqa: E501
import csv
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from .email_notifications import admin as email_notifications_admin

from api.models import (
    Chapter,
    Committee,
    Department,
    Feedback,
    Note,
    NoteUserAccess,
    Summary,
    Team,
    Tribe,
    User,
    FormResponse,
    Question,
    Form,
    FormAssignment,
    Cycle,
)


# fmt: off
class BaseModelAdmin(ImportExportModelAdmin):
    date_hierarchy = "date_updated"

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


RESOURCE_FIELDS = {
    "leader": fields.Field(
        column_name="leader",
        attribute="leader",
        widget=ForeignKeyWidget(User, field="email"),
    ),
    "owner": fields.Field(
        column_name="owner",
        attribute="owner",
        widget=ForeignKeyWidget(User, field="name"),
    ),
    "department": fields.Field(
        column_name="department",
        attribute="department",
        widget=ForeignKeyWidget(Department, field="name"),
    ),
    "team": fields.Field(
        column_name="team",
        attribute="team",
        widget=ForeignKeyWidget(Team, field="name"),
    ),
    "chapter": fields.Field(
        column_name="chapter",
        attribute="chapter",
        widget=ForeignKeyWidget(Chapter, field="name"),
    ),
    "tribe": fields.Field(
        column_name="tribe",
        attribute="tribe",
        widget=ForeignKeyWidget(Tribe, field="name"),
    ),
    "committee": fields.Field(
        column_name="committee",
        attribute="committee",
        widget=ForeignKeyWidget(Committee, field="name"),
    ),
    "mentioned_users": fields.Field(
        column_name="mentioned_users",
        attribute="mentioned_users",
        widget=ManyToManyWidget(User, field="name"),
    ),
    "linked_notes": fields.Field(
        column_name="linked_notes",
        attribute="linked_notes",
        widget=ManyToManyWidget(Note, field="title"),
    ),
    "note": fields.Field(
        column_name="note",
        attribute="note",
        widget=ForeignKeyWidget(Note, field="uuid"),
    )
}


class BaseModelResource(resources.ModelResource):
    lookup_field = "name"

    def get_instance(self, instance_loader, row):
        field_value = row.get(self.lookup_field)
        if field_value:
            try:
                return self._meta.model.objects.get(**{self.lookup_field: field_value})
            except self._meta.model.DoesNotExist:
                return None
        return None

@admin.register(Cycle)
class CycleAdmin(BaseModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")

@admin.register(Department)
class DepartmentAdmin(BaseModelAdmin):
    list_display = ("name", "date_created", "date_updated")
    fields = ("uuid", "name", "description", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name"]
    search_help_text = "جستجو در نام دپارتمان"


@admin.register(Tribe)
class TribeAdmin(BaseModelAdmin):
    class TribeResource(BaseModelResource):
        leader = RESOURCE_FIELDS["leader"]
        department = RESOURCE_FIELDS["department"]

        class Meta:
            model = Tribe
            fields = ("name", "leader", "department")

    resource_class = TribeResource
    list_display = ("name", "department", "leader", "date_created", "date_updated",)
    fields = ("uuid","name", ("department", "leader"), "description", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name", "department__name", "leader__name", "leader__email"]
    search_help_text = "جستجو در نام قبیله، نام دپارتمان، نام لیدر، ایمیل لیدر "


@admin.register(Chapter)
class ChapterAdmin(BaseModelAdmin):
    list_display = ("name", "department", "leader", "date_created", "date_updated",)
    fields = ("uuid", "name", ("department", "leader"), "description", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name", "department__name", "leader__name", "leader__email"]
    search_help_text = "جستجو در نام چپتر، نام دپارتمان، نام لیدر، ایمیل لیدر "


@admin.register(Team)
class TeamAdmin(BaseModelAdmin):
    class TeamResource(BaseModelResource):
        leader = RESOURCE_FIELDS["leader"]
        department = RESOURCE_FIELDS["department"]
        tribe = RESOURCE_FIELDS["tribe"]

        class Meta:
            model = Team
            fields = ("name", "leader", "department", "tribe")

    resource_class = TeamResource
    list_display = ("name", "department", "leader", "tribe", "date_created", "date_updated",)
    fields = ("uuid", "name", ("department", "leader", "tribe"), "description", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name", "department__name", "leader__name", "leader__email"]
    search_help_text = "جستجو در نام تیم، نام دپارتمان، نام لیدر، ایمیل لیدر "


@admin.register(Committee)
class CommitteeAdmin(BaseModelAdmin):
    list_display = ("name", "date_created", "date_updated",)
    fields = ("uuid", "name", "description", "members", ("date_created", "date_updated"),)
    filter_horizontal = ("members",)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name"]
    search_help_text = "جستجو در نام کمیته"


@admin.register(User)
class UserAdmin(BaseModelAdmin):
    class UserResource(BaseModelResource):
        leader = RESOURCE_FIELDS["leader"]
        department = RESOURCE_FIELDS["department"]
        team = RESOURCE_FIELDS["team"]
        chapter = RESOURCE_FIELDS["chapter"]
        committee = RESOURCE_FIELDS["committee"]
        lookup_field = "email"

        class Meta:
            model = User
            import_id_fields = ("email",)
            fields = ("email", "name", "gmail", "phone", "leader", "level", "department", "team", "chapter",)

    resource_class = UserResource
    list_display = ("email", "name", "phone", "department", "chapter", "team", "leader", "agile_coach", "date_created", "date_updated",)
    fields = ("uuid", "name", "phone", ("email", "gmail"), ("department", "chapter", "team", "level", "leader", "agile_coach", "committee"), ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "email")
    search_fields = ["email", "name", "phone"]
    search_help_text = "جستجو در نام کاربر، ایمیل، موبایل"


@admin.register(Note)
class NoteAdmin(BaseModelAdmin):
    class NoteResource(BaseModelResource):
        owner = RESOURCE_FIELDS["owner"]
        mentioned_users = RESOURCE_FIELDS["mentioned_users"]
        linked_notes = RESOURCE_FIELDS["linked_notes"]
        lookup_field = "uuid"

        class Meta:
            model = Note
            fields = ("uuid", "owner", "title", "content", "date", "type", "mentioned_users", "linked_notes",)

    resource_class = NoteResource
    list_display = ("title", "type", "owner", "date", "submit_status", "date_created", "date_updated")
    fields = ( "uuid", ("title", "type"), ("owner", "date", "period", "year"), "content", "mentioned_users", "is_public", "submit_status", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated", "mentioned_users")
    ordering = ("-date_updated", "title")
    search_fields = ["uuid", "title", "owner__name", "owner__email"]
    search_help_text = "جستجو در عنوان، نام نویسنده، ایمیل نویسنده"


@admin.register(Feedback)
class FeedbackAdmin(BaseModelAdmin):
    list_display = ("uuid", "owner", "note", "date_created", "date_updated")
    fields = ("uuid", ("owner", "note"), "content", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["owner__name", "owner__email", "note__title"]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت"

@admin.register(Summary)
class SummaryAdmin(BaseModelAdmin):
    class SummaryResource(BaseModelResource):
        note = RESOURCE_FIELDS["note"]

        class Meta:
            model = Summary
            fields = ("uuid", "note", "content", "performance_label", "ladder_change", "bonus", "salary_change", "committee_date",)
    resource_class = SummaryResource
    list_display = ("uuid", "note", "performance_label", "committee_date", "submit_status", "date_created", "date_updated")
    fields = ("uuid", "note", "content", "performance_label", "ladder_change", "bonus", "salary_change", "committee_date", "submit_status", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["note__title", "note__owner__name", "note__owner__email"]
    search_help_text = "جستجو در عنوان یادداشت، نام نویسنده، ایمیل نویسنده"


@admin.register(NoteUserAccess)
class NoteUserAccessAdmin(BaseModelAdmin):
    list_display = ("uuid", "note", "user", "can_view", "can_edit", "can_view_summary", "can_write_summary", "can_write_feedback", "can_view_feedbacks", "date_created", "date_updated",)
    fields = ("uuid", "note", "user", "can_view", "can_edit", "can_view_summary", "can_write_summary", "can_write_feedback", "can_view_feedbacks", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["user__name", "user__email", "note__title"]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت"

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('question_text', 'scale_min', 'scale_max')
    readonly_fields = ()

class FormAssignmentInline(admin.TabularInline):
    model = FormAssignment
    extra = 1
    fields = ('assigned_to', 'message', 'deadline', 'is_completed', 'assigned_by')
    readonly_fields = ('is_completed', 'assigned_by')   

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_default', 'form_type', 'cycle')
    list_filter = ('form_type', 'is_default')
    search_fields = ('name', 'description')
    inlines = [QuestionInline, FormAssignmentInline]
    actions = ['export_skipped_users_csv']

    def save_related(self, request, form, formsets, change):
        """
        Validate inline assignments for default forms during the save process.
        Default forms should not accept manual assignment.
        """
        obj = form.instance 
        if obj.is_default:
            # Check all inline FormAssignment entries
            for formset in formsets:
                for inline_form in formset.forms:
                    if inline_form.cleaned_data and not inline_form.cleaned_data.get('DELETE', False):
                        assigned_to = inline_form.cleaned_data.get('assigned_to')
                        if assigned_to:
                            raise ValidationError(
                                "Manual assignment to default forms is not allowed. Default forms are assigned automatically."
                            )
        super().save_related(request, form, formsets, change)

    def save_formset(self, request, form, formset, change):
        """
        Override save_formset to ensure `assigned_by` is set for non-default forms.
        """
        instances = formset.save(commit=False)

        for instance in instances:
            if instance.form.is_default:
                continue

            if isinstance(instance, FormAssignment):

                if not getattr(instance, "assigned_by_id", None):
                    instance.assigned_by = request.user

            instance.save()

        formset.save_m2m()

        instances = formset.save(commit=False)  # Fetch unsaved formset instances

        for instance in instances:
            # Skip saving for default forms, as the signal handles these
            if instance.form.is_default:
                continue

            # Ensure `assigned_by` is set for non-default forms
            if isinstance(instance, FormAssignment) and not instance.assigned_by:
                instance.assigned_by = request.user

            instance.save()

        formset.save_m2m()  # Save many-to-many relationships, if any

    def calculate_user_assignments(self, form, check_existing_assignments=True):
        """
        Calculate affected and skipped users for a given form.
        Returns two lists: affected_users and skipped_users.

        Args:
            form (Form): The form instance being processed.
            check_existing_assignments (bool): Whether to check for existing assignments in the database.
        """
        users = User.objects.all()
        affected_users = []
        skipped_users = []

        for user in users:
            if check_existing_assignments and FormAssignment.objects.filter(form=form, assigned_to=user).exists():
                skipped_users.append({"user": user, "reason": "Already assigned"})
                continue

            if form.form_type == Form.FormType.TL:
                leaders = user.get_leaders()
                if not leaders:
                    skipped_users.append({"user": user, "reason": "No leader assigned"})
                    continue
                affected_users.append(user)

            elif form.form_type == Form.FormType.PM:              # FUTURE ENHANCEMENT: automated assignment for PMs
                skipped_users.append({"user": user, "reason": "Manual assignment required"})
                continue

            else:
                skipped_users.append({"user": user, "reason": "This form type is not applicable"})

        return affected_users, skipped_users
    
    def save_model(self, request, obj, form, change):
        """
        Override save_model to handle default form assignment notification.
        """ 
        super().save_model(request, obj, form, change)
        if obj.is_default and obj.cycle.is_active:
            # Exclude `Already Assigned` instances for the instant notification in admin panel
            affected_users, skipped_users = self.calculate_user_assignments(obj, check_existing_assignments=False)

            # Notify the admin with a summary
            self.message_user(
                request,
                f"Form '{obj.name}' processed. Affected: {len(affected_users)} users. "
                f"Skipped: {len(skipped_users)} users.",
                level="info"
            )


    def export_skipped_users_csv(self, request, queryset):
        """
        Export skipped users as a CSV file for selected forms.
        """
        if not queryset:
            self.message_user(request, "No forms selected.", level="warning")
            return
        
        # Create CSV response
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="skipped_users.csv"'},
        )
        writer = csv.writer(response)
        writer.writerow(["Form Name", "User Email", "User Name", "Reason Skipped"])

        # Iterate over selected forms
        skipped_count = 0

        for form in queryset:
            _, skipped_users = self.calculate_user_assignments(form)

            for entry in skipped_users:
                user = entry["user"]
                writer.writerow([form.name, user.email, user.name, entry["reason"]])
                skipped_count += 1

        if skipped_count == 0:
            self.message_user(request, "No skipped users to export for the selected forms.", level="info")
            return

        self.message_user(
            request,
            f"Exported skipped users for {skipped_count} entries across selected forms.",
            level="success"
        )

        return response

    export_skipped_users_csv.short_description = "Export Skipped Users to CSV"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'scale_min', 'scale_max', 'category', 'form')
    list_filter = ['form']
    search_fields = ('question_text', 'form__name')

@admin.register(FormResponse)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'form', 'question', 'get_answer_display')
    list_filter = ('form', 'question', 'user')
    search_fields = ('user__username', 'form__name', 'question__question_text')
    readonly_fields = ('get_answer_display',)
   
    def get_answer_display(self, obj):
        return obj.get_answer_display()
    get_answer_display.short_description = 'Answer'

    # Grouping for better UX
    fieldsets = (
        ("Response Information", {
            'fields': ('user', 'form', 'question')
        }),
        ("Answer Details", {
            'fields': ('answer', 'get_answer_display')
        }),
    )

    def get_answer_display(self, obj):
        return obj.get_answer_display()
    get_answer_display.short_description = 'Answer'

@admin.register(FormAssignment)
class FormAssignmentAdmin(admin.ModelAdmin):
    list_display = ("form", "assigned_to", "assigned_by", "deadline", "is_completed")
    list_filter = ("form", "is_completed")
    search_fields = ("assigned_to__email", "form__name")

                           
# fmt: on
