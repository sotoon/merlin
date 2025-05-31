import csv

from django.http import HttpResponse
from django.contrib import admin
from django.core.exceptions import ValidationError

from api.utils import calculate_form_results
from api.models import(
    Question,
    Form,
    FormAssignment,
    FormResponse,
    User
)


__all__ = ['QuestionInline', 'FormAssignmentInline', 'FormAdmin', 'QuestionAdmin', 
           'ResponseAdmin', 'FormAssignmentAdmin']


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
    actions = ['export_skipped_users_csv', 'export_form_results']

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

    def export_form_results(self, request, queryset):
        """
        Export each assessed user's category and question averages
        for the selected forms, in long format.
        """
        if not queryset:
            self.message_user(request, "No forms selected.", level="warning")
            return

        # Prepare CSV response
        response = HttpResponse(
            content_type="text/csv",
            headers={'Content-Disposition': 'attachment; filename="form_results.csv"'},
        )
        writer = csv.writer(response)

        # Header row
        writer.writerow([
            "Form Name",
            "Assessed User",
            "Type",
            "Item",
            "Average"
        ])

        for form in queryset:
            # find all distinct assessed_by IDs for this form
            assignments = FormAssignment.objects.filter(form=form)
            assessed_ids = assignments.values_list("assigned_by", flat=True).distinct()

            for assessed_id in assessed_ids:
                # lookup the assessed user
                try:
                    assessed_user = User.objects.get(id=assessed_id)
                except User.DoesNotExist:
                    continue

                # gather all responses for that assessed user in this form
                to_users = assignments.filter(assigned_by=assessed_id)\
                                      .values_list("assigned_to", flat=True)
                responses = FormResponse.objects.filter(
                    question__form=form,
                    user__in=to_users
                )

                # calculate aggregated results
                results = calculate_form_results(responses, form)

                # write category averages
                for category, avg in results["categories"].items():
                    writer.writerow([
                        form.name,
                        assessed_user.name,
                        "Category",
                        category,
                        f"{avg:.2f}" if avg is not None else ""
                    ])

                # write per‑question averages
                for q in results["questions"]:
                    writer.writerow([
                        form.name,
                        assessed_user.name,
                        "Question",
                        q["text"],
                        f"{q['average']:.2f}" if q["average"] is not None else ""
                    ])

        self.message_user(
            request,
            f"Exported results for {queryset.count()} form(s).",
            level="success"
        )
        return response

    export_form_results.short_description = "Export aggregated form results"


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

                           
