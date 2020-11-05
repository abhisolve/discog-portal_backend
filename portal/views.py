# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect
from django.views.generic import View, ListView
from assignments.models import Module, Enrollment, ModuleCategory, Resource, StaffDetail, ModuleLesson, Task
from discoauth.models import DiscoUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.crypto import get_random_string
from django.conf import settings
from discomail.models import EmailQueue
from discoauth.models import PasswordReset
from django.template.loader import render_to_string
from django.contrib import messages
from discomail.models import PlatformInvite


def staff_role(id):
    """
    helper function to find the staff_role of the user
    which will define his/her access level
    """
    try:
        staff_detail =  StaffDetail.objects.get(user__id=id)
        return staff_detail.staff_role
    except StaffDetail.DoesNotExist:
        return None


class Dashboard(LoginRequiredMixin, View):
    template_name = "dashboard/dashboard.html"

    def get(self, request):

        if request.user.is_teacher:
            user_role = staff_role(self.request.user.id)
            users = DiscoUser.objects.all()
            return render(request, self.template_name, context={'users': users,
                                                                'user_role': user_role, 'title': 'Dashboard'})
        elif request.user.is_student:
            return redirect('portal:student-dashboard')
        else:
            raise PermissionDenied("Only User with is_teacher permission set to True are allowed to access this endpoint")


class StudentDashboard(LoginRequiredMixin, View):
    template_name = "student-portal/student.html"

    def get(self, request):
        if request.user.is_student:
            student_modules = Enrollment.objects.filter(student=request.user)
            return render(request, self.template_name, context={'modules': student_modules})
        else:
            raise PermissionDenied("Only Student are allowed to access this page")


class InProgressModule(LoginRequiredMixin, View):
    template_name = 'student-portal/in-progress-module.html'

    def get(self, request):
        if request.user.is_student:
            try:
                in_progress_enrollment = Enrollment.objects.get(student__id=request.user.id,
                                                                enrollment_status="IN-PROGRESS")
                lessons = ModuleLesson.objects.filter(module=in_progress_enrollment.module).order_by('created_at')
                return render(request, self.template_name, context={'in_progress_enrollment': in_progress_enrollment,
                                                                    'date_started': in_progress_enrollment.date_to_start,
                                                                    'in_progress_lessons': lessons})
            except Enrollment.DoesNotExist:
                return render(request, self.template_name, context={'in_progress_enrollment': None,
                                                                    'date_started': None})
        else:
            raise PermissionDenied("Only Student account are allowed to access this page")


class CompletedModuleList(LoginRequiredMixin, ListView):
    template_name = 'student-portal/completed-modules.html'
    model = Module
    paginate_by = 6
    context_object_name = 'modules'

    def get_queryset(self):
        if self.request.user.is_student:
            modules_id = Enrollment.objects.filter(enrollment_status="COMPLETED", student_id=self.request.user.id, module__status='PUBLISHED').values_list('module_id', flat=True)
            return Module.objects.filter(id__in=modules_id)
        else:
            return Module.objects.none()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module_lessons'] = ModuleLesson.objects.filter(module__in=self.get_queryset()).order_by('created_at')
        context['lesson_tasks'] = Task.objects.filter(lesson__module__in=self.get_queryset())
        return context


class ResetPassword(View):
    template_name = 'dashboard/reset-password.html'

    def get(self, request):
        return render(request, self.template_name, context={})


class AssignmentsDashboard(LoginRequiredMixin, View):
    template_name = 'dashboard/assignments-dashboard.html'

    def get(self, request):
        user_role = staff_role(self.request.user.id)                
        if request.user.is_teacher or user_role == "MAN" or user_role == "CC":
            return render(request, self.template_name, context={})
        else:
            raise PermissionDenied("Only Teacher accounts are allowed to access this page")


class SpecificAssignmentsDashboard(LoginRequiredMixin, View):
    template_name = 'dashboard/specific-assignments-dashboard.html'

    def get(self, request, pk):
        user_role = staff_role(self.request.user.id)
        if request.user.is_teacher or user_role == "MAN" or user_role == "CC":
            moduleIds = Enrollment.objects.filter(student_id=pk).values_list('module_id', flat=True)
            student_name = DiscoUser.objects.filter(id=pk).values_list('first_name', flat=True)[0]
            modules = Module.objects.filter(status="PUBLISHED").exclude(id__in=moduleIds)
            module_category = ModuleCategory.objects.filter(id__in=Module.objects.filter(status="PUBLISHED").exclude(id__in=moduleIds).values_list('module_category_id', flat=True))
            return render(request, self.template_name,
                          context={"modules": modules, "module_categories": module_category, "name": student_name})
        else:
            raise PermissionDenied("Only Teacher accounts are allowed to access this page")


class UserAccountDashboard(LoginRequiredMixin, View):
    template_name = "dashboard/user-account-dashboard.html"

    def get(self, request):
        user_role = staff_role(self.request.user.id)
        
        if request.user.is_teacher or user_role == "MAN":
            return render(request, self.template_name, context={'title': 'User Accounts Dasboard'})
        else:
            raise PermissionDenied("only teacher accounts are allowed to access this page")


class ResourceDashboard(LoginRequiredMixin, View):
    template_name = 'student-portal/resource.html'

    def get(self, request):
        if request.user.is_student:
            if self.request.user.resources.exists():
                resources = self.request.user.resources.all().order_by('id')[:9:1]
                return render(request, self.template_name, context={'resources': resources})
            else:
                return render(request, self.template_name, context={})
        else:
            raise PermissionDenied("Only Students accounts are allowed to access this page")


class SpecificResourceDashboard(LoginRequiredMixin, View):
    template_name = 'dashboard/specific-resource.html'

    def get(self, request, pk):
        if request.user.is_student:
            specificResource = Resource.objects.get(id=pk)
            return render(request, self.template_name, context={'resource': specificResource})
        else:
            raise PermissionDenied("Only students accounts are allowed to access this page")


class ReviewStudentsDashboard(LoginRequiredMixin, View):
    template_name = 'dashboard/review-students-page.html'

    def get(self, request):
        user_role = staff_role(self.request.user.id)
                                   
        if request.user.is_admin or user_role == "MAN" or user_role == "MOD":
            return render(request, self.template_name, context={'title': 'In Review Students'})
        else:
            raise PermissonDenied("Only Admin accounts or Teacher accounts are allowed to access this page")


class ReviewModulesDashboard(LoginRequiredMixin, View):
    template_name = 'dashboard/review-modules-page.html'

    def get(self, request, pk):
        user_role = staff_role(self.request.user.id)
        if request.user.is_admin or user_role == "MAN" or user_role == "MOD":
            return render(request, self.template_name, context={'title': 'In Review Modules'})
        else:
            raise PermissonDenied("Only Admin accounts or Teachers accounts are allowed to access this page")


class ReviewTasksDashboard(LoginRequiredMixin, View):
    template_name = 'dashboard/review-tasks-page.html'

    def get(self, request, pk):
        user_role = staff_role(self.request.user.id)
        if request.user.is_admin or user_role == "MAN" or user_role == "MOD":
            return render(request, self.template_name, context={'title': 'In Review Tasks'})
        else:
            raise PermissionDenied("Only Admin accounts or Teacher accounts are allowed to access this page")


class StaffDashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard/staff-dashboard.html'

    def get(self, request):
        if request.user.is_teacher or request.user.is_staff:
            return render(request, self.template_name, context={'title': 'Staff Dashboard'})
        else:
            raise PermissonDenied("Only Teachers accounts or superadmin accounts are allowed to access this page")


class AddResourcePageView(LoginRequiredMixin, View):
    template_name = "dashboard/add-resource-page.html"

    def get(self, request):
        users = DiscoUser.objects.filter(is_student=True, is_active=True)
        if request.user.is_admin or request.user.is_teacher:
            return render(request, self.template_name, context={'students': users, 'title': 'Add Resource'})
        else:
            raise PermissionDenied("Only Teachers accounts or superadmin accounts are allowed to access this page")


class ViewResourcePage(LoginRequiredMixin, View):
    template_name = "student-portal/view-resource.html"

    def get(self, request, pk):
        try:
            resource_data = Resource.objects.get(id=pk)
            if request.user.is_student:
                return render(request, self.template_name, context={'resource_data': resource_data})
            else:
                raise PermissionDenied("Only Student accounts are allowed to access this page")
        except ResourceData.DoesNotExist:
            raise Http404("Resource File does not Exist")


class SendResetPasswordMail(LoginRequiredMixin, View):
    template_name = 'student-portal/reset-password.html'

    def get(self, request):
        password_reset_hash = get_random_string(length=100)
        if PasswordReset.objects.filter(is_active=True, user=request.user).count() >= 1:
            return render(request, self.template_name, context={'message': "We have already sent you an email please check again."})
        else:
            password_reset_instance = PasswordReset.objects.create(is_active=True, user=request.user, password_hash=password_reset_hash)
            EmailQueue.objects.create(subject='Reset password',
                                      to_email=request.user.email,
                                      body=render_to_string('discomail/reset-password.html',
                                                            context={'data': password_reset_instance}),
                                      from_email=settings.SENDER_MAIL, send_now=False)
            return render(request, self.template_name, context={'message': "An email with password reset instructions has been sent to your email address."})


class ResourceManagerPage(LoginRequiredMixin, View):
    template_name = 'dashboard/resource-manager.html'

    def get(self, request):
        if request.user.is_admin or request.user.is_teacher:
            return render(request, self.template_name, context={'title': 'Resource Manager'})
        else:
            raise PermissionDenied("Only Teacher accounts or SuperAdmin accounts are allowed to access this page.")


class EditStudentAccountPage(LoginRequiredMixin, View):
    template_name = 'student-portal/edit-account.html'

    def get(self, request):
        if request.user.is_student:
            return render(request, self.template_name)
        else:
            raise PermissionDenied("Only student accounts are allowed to access this page.")

class ForgotPasswordPage(LoginRequiredMixin, View):
    template_name = 'student-portal/forgot-password.html'

    def get(self, request):
        if request.user.is_student:
            return render(request, self.template_name)
        else:
            raise PermissionDenied("Only student accounts are allowed to access this page.")


class SetPasswordPage(LoginRequiredMixin, View):
    template_name = 'student-portal/set-password.html'

    def get(self, request):
        if request.user.is_student:
            return render(request, self.template_name)
        else:
            raise PermissionDenied("Only student accounts are allowed to access this page.")


class EditResourcePage(LoginRequiredMixin, View):
    template_name = 'dashboard/edit-resource.html'

    def get(self, request, pk):
        if request.user.is_teacher or request.user.is_admin or user_role == "MAN" or user_role == "CC":
            try:
                resource = Resource.objects.get(id=pk)
                users = DiscoUser.objects.filter(is_student=True, is_active=True).exclude(id__in=resource.users.all())
                return render(request, self.template_name, context={'resource': resource, 'students': users, 'title': 'Edit Resource'})
            except Resource.DoesNotExist:
                raise Http404("Resource does not Exist")
        else:
            raise PermissionDenied("Only Admin and Teacher accounts are allowed to access this page.")


class ResourceFilesPage(LoginRequiredMixin, View):
    template_name = 'dashboard/resource-files.html'

    def get(self, request):
        if request.user.is_teacher or request.user.is_admin or user_role == "MAN" or user_role == "CC":
            return render(request, self.template_name)
        else:
            raise PermissionDenied("Only admin and Teacher accounts are allowed to access this page.")


class PlatformInviteView(View):
    """
    view used to provide the platform invite
    funcitonality
    """
    template_name = 'discoauth/platform-invite.html'

    def get(self, request, invite_hash, *args, **kwargs):
        try:
            platform_invite = PlatformInvite.objects.get(invite_hash=invite_hash)
            return render(request, self.template_name, context={'platform_invite': platform_invite})
        except PlatformInvite.DoesNotExist:
            raise Http404("Requested Page Does Not Exist")

    def post(self, request, invite_hash,  *args, **kwargs):
        try:
            invite = PlatformInvite.objects.get(invite_hash=invite_hash)
            user = invite.user
            if request.POST.get('password', True) == request.POST.get('re_password', False):
                # set the user password
                user.set_password(request.POST.get('password', None))
                user.save()
                # update the invite update to True
                # just to make sure, That this invite
                # has been used
                invite.used = True
                invite.save()
                messages.info(request, "Login using your email and password set by you in previous page", extra_tags="alert-success")
                return redirect("discoauth:login", permanent=False)
            else:
                messages.error(request, "Password and Re-password fileds doesn't match", extra_tags="alert-danger")
                return redirect("portal:platform-invite", permanent=False, **{'invite_hash': invite_hash})
        except PlatformInvite.DoesNotExist:
            raise Http404("Requested Page Does Not Exist")
