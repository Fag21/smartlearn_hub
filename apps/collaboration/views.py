from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView

from .models import (
    Assignment,
    ChatMessage,
    GroupMember,
    SharedResource,
    StudyGroup,
)


@method_decorator(login_required, name="dispatch")
class StudyGroupListView(ListView):
    model = StudyGroup
    template_name = "collaboration/study_group_list.html"
    context_object_name = "groups"

    def get_queryset(self):
        user = self.request.user
        # Show groups the user is in or public groups
        return StudyGroup.objects.filter(
            Q(visibility="public")
            | Q(creator=user)
            | Q(members__user=user, members__is_active=True)
        ).distinct()


@method_decorator(login_required, name="dispatch")
class StudyGroupCreateView(CreateView):
    model = StudyGroup
    template_name = "collaboration/study_group_form.html"
    fields = [
        "name",
        "description",
        "course",
        "visibility",
        "max_members",
        "allow_join_requests",
        "allow_member_invites",
    ]

    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        # Add creator as admin member
        GroupMember.objects.get_or_create(
            group=self.object, user=self.request.user, defaults={"role": "admin"}
        )
        messages.success(self.request, "Study group created successfully!")
        return response


@method_decorator(login_required, name="dispatch")
class StudyGroupDetailView(DetailView):
    model = StudyGroup
    template_name = "collaboration/study_group_detail.html"
    context_object_name = "group"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        user = self.request.user
        context["is_member"] = group.members.filter(user=user, is_active=True).exists()
        context["members"] = group.members.select_related("user")
        context["messages"] = group.messages.select_related("user").all()
        context["resources"] = group.resources.all()
        context["assignments"] = group.assignments.all()
        return context


@login_required
def join_study_group(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)

    if group.is_full:
        messages.error(request, "This group is full.")
        return redirect("collaboration:study_group_detail", pk=pk)

    member, created = GroupMember.objects.get_or_create(
        group=group, user=request.user, defaults={"role": "member"}
    )
    if not created and not member.is_active:
        member.is_active = True
        member.save()

    messages.success(request, "You have joined the study group.")
    return redirect("collaboration:study_group_detail", pk=pk)


@login_required
def leave_study_group(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    member = GroupMember.objects.filter(group=group, user=request.user).first()

    if not member:
        messages.error(request, "You are not a member of this group.")
    else:
        # Do not allow the creator to leave their own group
        if group.creator == request.user:
            messages.error(request, "Group creators cannot leave their own group.")
        else:
            member.is_active = False
            member.save()
            messages.success(request, "You have left the study group.")

    return redirect("collaboration:study_group_detail", pk=pk)


@login_required
def send_chat_message(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            ChatMessage.objects.create(group=group, user=request.user, content=content)
            messages.success(request, "Message sent.")
        else:
            messages.error(request, "Message cannot be empty.")

    return redirect("collaboration:study_group_detail", pk=pk)


@login_required
def group_resources(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    resources = group.resources.all()
    return render(
        request,
        "collaboration/group_resources.html",
        {"group": group, "resources": resources},
    )


@login_required
def upload_resource(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        url = request.POST.get("url", "").strip()
        file = request.FILES.get("file")

        if not title:
            messages.error(request, "Title is required.")
        else:
            SharedResource.objects.create(
                group=group,
                uploaded_by=request.user,
                title=title,
                description=description,
                url=url,
                file=file,
            )
            messages.success(request, "Resource uploaded successfully.")
            return redirect("collaboration:group_resources", pk=pk)

    return render(request, "collaboration/upload_resource.html", {"group": group})


@login_required
def group_assignments(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    assignments = group.assignments.all()
    return render(
        request,
        "collaboration/group_assignments.html",
        {"group": group, "assignments": assignments},
    )


@login_required
def create_assignment(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        due_date = request.POST.get("due_date")
        max_points = request.POST.get("max_points") or 100

        if not title or not due_date:
            messages.error(request, "Title and due date are required.")
        else:
            try:
                due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                messages.error(request, "Invalid due date format.")
            else:
                Assignment.objects.create(
                    group=group,
                    created_by=request.user,
                    title=title,
                    description=description,
                    due_date=due_dt,
                    max_points=int(max_points),
                )
                messages.success(request, "Assignment created successfully.")
                return redirect("collaboration:group_assignments", pk=pk)

    return render(request, "collaboration/create_assignment.html", {"group": group})