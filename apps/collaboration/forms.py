from django import forms

from .models import Assignment, SharedResource, StudyGroup


class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = [
            "name",
            "description",
            "course",
            "visibility",
            "max_members",
            "allow_join_requests",
            "allow_member_invites",
        ]


class SharedResourceForm(forms.ModelForm):
    class Meta:
        model = SharedResource
        fields = ["title", "description", "file", "url", "resource_type"]


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "due_date", "max_points", "allow_late_submissions", "allow_resubmissions"]